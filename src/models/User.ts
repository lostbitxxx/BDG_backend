import { MongoClient, Db, Collection, ObjectId } from 'mongodb';

// ─── Connection ───────────────────────────────────────────────
let cachedDb: Db | null = null;

async function getDb(): Promise<Db> {
  if (cachedDb) return cachedDb;
  const client = await MongoClient.connect(process.env.MONGODB_URI as string);
  cachedDb = client.db(process.env.DB_NAME || 'bodongsgua');
  console.log('✅ Connected to MongoDB');
  return cachedDb;
}

// ─── Types ────────────────────────────────────────────────────
export interface User {
  _id?: string;
  email: string;
  password: string;
  firstName: string;
  lastName: string;
  isEmailVerified: boolean;
  createdAt: Date;
  updatedAt: Date;
  lastLoginAt?: Date;
}

type NewUserData = Omit<User, '_id' | 'createdAt' | 'updatedAt'>;

// ─── Model ────────────────────────────────────────────────────
export class UserModel {
  private static async col(): Promise<Collection<User>> {
    const db = await getDb();
    return db.collection<User>('users');
  }

  static async createUser(data: NewUserData): Promise<User> {
    const col = await this.col();
    const user: User = { ...data, createdAt: new Date(), updatedAt: new Date() };
    const result = await col.insertOne(user);
    return { ...user, _id: result.insertedId.toString() };
  }

  static async findUserByEmail(email: string): Promise<User | null> {
    const col = await this.col();
    return col.findOne({ email: email.toLowerCase() }) as Promise<User | null>;
  }

  static async findUserById(id: string): Promise<User | null> {
    const col = await this.col();
    return col.findOne({ _id: new ObjectId(id) as any }) as Promise<User | null>;
  }

  static async updateUser(email: string, updates: Partial<User>): Promise<void> {
    const col = await this.col();
    await col.updateOne(
      { email: email.toLowerCase() },
      { $set: { ...updates, updatedAt: new Date() } }
    );
  }

  static async updateLastLogin(email: string): Promise<void> {
    await this.updateUser(email, { lastLoginAt: new Date() });
  }
}