import { Server as SocketIOServer } from 'socket.io';
import { Server as HTTPServer } from 'http';
import { sendToAI } from '../services/openRouter';
import { textToSpeech } from '../services/elevenLabs';

interface ChatMessage {
  role: 'system' | 'user' | 'assistant';
  content: string;
}

interface User {
  id: string;
  username: string;
  character?: string;
}

interface Room {
  id: string;
  users: Map<string, User>;
}

// Store active rooms
const rooms = new Map<string, Room>();

export function setupSocketIO(httpServer: HTTPServer) {
  const io = new SocketIOServer(httpServer, {
    cors: {
      origin: '*',
      methods: ['GET', 'POST'],
    },
  });

  io.on('connection', (socket) => {
    console.log('Client connected:', socket.id);

    // Join a chat room
    socket.on('join_room', (data: { roomId: string; user: User }) => {
      const { roomId, user } = data;
      socket.join(roomId);
      
      // Create room if doesn't exist
      if (!rooms.has(roomId)) {
        rooms.set(roomId, {
          id: roomId,
          users: new Map(),
        });
      }
      
      const room = rooms.get(roomId)!;
      room.users.set(socket.id, user);
      
      // Notify others
      socket.to(roomId).emit('user_joined', {
        user,
        users: Array.from(room.users.values()),
      });
      
      // Send current users to the joiner
      socket.emit('room_users', {
        users: Array.from(room.users.values()),
      });
      
      console.log(`User ${user.username} joined room ${roomId}`);
    });

    // Handle chat message
    socket.on('send_message', async (data: { roomId: string; message: string; character: string }) => {
      const { roomId, message, character } = data;
      
      // Get room
      const room = rooms.get(roomId);
      if (!room) return;
      
      const user = room.users.get(socket.id);
      if (!user) return;
      
      // Emit user message first
      io.to(roomId).emit('receive_message', {
        id: Date.now().toString(),
        role: 'user',
        content: message,
        username: user.username,
        timestamp: new Date().toISOString(),
      });

      // Create conversation history for AI
      const systemPrompt = getSystemPrompt(character);
      const messages = [
        { role: 'system' as const, content: systemPrompt },
        { role: 'user' as const, content: message },
      ];

      // Send to AI
      const aiResponse = await sendToAI(messages);
      
      if (aiResponse.success && aiResponse.message) {
        // Emit AI response
        io.to(roomId).emit('receive_message', {
          id: (Date.now() + 1).toString(),
          role: 'assistant',
          content: aiResponse.message,
          username: character || 'Learning Companion',
          timestamp: new Date().toISOString(),
        });

        // Optionally generate TTS (disabled for now - needs S3)
        // await textToSpeech(aiResponse.message);
      }
    });

    // Typing indicator
    socket.on('typing', (data: { roomId: string; isTyping: boolean }) => {
      socket.to(data.roomId).emit('user_typing', {
        userId: socket.id,
        isTyping: data.isTyping,
      });
    });

    // Leave room
    socket.on('leave_room', (roomId: string) => {
      socket.leave(roomId);
      
      const room = rooms.get(roomId);
      if (room) {
        const user = room.users.get(socket.id);
        room.users.delete(socket.id);
        
        if (user) {
          socket.to(roomId).emit('user_left', {
            user,
            users: Array.from(room.users.values()),
          });
        }
      }
    });

    // Disconnect
    socket.on('disconnect', () => {
      console.log('Client disconnected:', socket.id);
      
      // Remove user from all rooms
      rooms.forEach((room, roomId) => {
        if (room.users.has(socket.id)) {
          const user = room.users.get(socket.id);
          room.users.delete(socket.id);
          
          if (user) {
            io.to(roomId).emit('user_left', {
              user,
              users: Array.from(room.users.values()),
            });
          }
        }
      });
    });
  });

  return io;
}

// System prompt based on character personality
function getSystemPrompt(character: string): string {
  const prompts: Record<string, string> = {
    'encouraging': `You are an encouraging Mandarin tutor. You are warm, supportive, and always motivate the learner. 
    You provide positive feedback and gentle corrections. Use emojis occasionally. Keep responses concise and helpful.
    You help with Putonghua (Mandarin) pronunciation, tones, and conversation.`,
    
    'responsible': `You are a responsible and thorough Mandarin tutor. You are precise, patient, and detail-oriented.
    You explain grammar and pronunciation rules clearly. Provide structured feedback. Keep responses educational.
    You help with Putonghua (Mandarin) pronunciation, tones, and conversation.`,
    
    'teasing': `You are a playful, teasing Mandarin tutor. You are friendly but like to joke around.
    You give feedback with humor but still help improve pronunciation. Make learning fun!
    You help with Putonghua (Mandarin) pronunciation, tones, and conversation.`,
  };
  
  return prompts[character] || prompts['encouraging'];
}

export default { setupSocketIO };
