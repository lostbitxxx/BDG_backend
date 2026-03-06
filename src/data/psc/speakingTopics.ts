/**
 * PSC Section 5 - Speaking Topics (命題說話)
 * 30 topics from official PSC topic list
 * Candidates choose 1 of 2 topics
 */

export interface SpeakingTopic {
  id: string;
  topic: string;
  description?: string;
  keywords?: string[];
}

export const speakingTopics: SpeakingTopic[] = [
  { id: "t1", topic: "我的愿望(或理想)", keywords: ["愿望", "理想", "未来", "目标"] },
  { id: "t2", topic: "我的学习生活", keywords: ["学习", "学校", "老师", "同学", "课堂"] },
  { id: "t3", topic: "我尊敬的人", keywords: ["尊敬", "敬佩", "榜样", "父母", "老师"] },
  { id: "t4", topic: "我喜爱的动物(或植物)", keywords: ["动物", "植物", "喜欢", "宠物", "花"] },
  { id: "t5", topic: "童年的记忆", keywords: ["童年", "回忆", "玩耍", "成长", "趣事"] },
  { id: "t6", topic: "我喜爱的职业", keywords: ["职业", "工作", "梦想", "选择", "未来"] },
  { id: "t7", topic: "难忘的旅行", keywords: ["旅行", "旅游", "经历", "风景", "见闻"] },
  { id: "t8", topic: "我的朋友", keywords: ["朋友", "友谊", "相处", "往事", "回忆"] },
  { id: "t9", topic: "我喜爱的文学(或其他)艺术形式", keywords: ["文学", "艺术", "书籍", "音乐", "电影"] },
  { id: "t10", topic: "谈谈卫生与健康", keywords: ["卫生", "健康", "锻炼", "饮食", "习惯"] },
  { id: "t11", topic: "我的业余生活", keywords: ["业余", "爱好", "休闲", "活动", "放松"] },
  { id: "t12", topic: "我喜欢的季节(或天气)", keywords: ["季节", "天气", "春", "夏", "秋", "冬"] },
  { id: "t13", topic: "学习普通话的体会", keywords: ["普通话", "学习", "发音", "声调", "困难"] },
  { id: "t14", topic: "谈谈服饰", keywords: ["服饰", "穿着", "搭配", "时尚", "审美"] },
  { id: "t15", topic: "我的假日生活", keywords: ["假日", "周末", "假期", "安排", "活动"] },
  { id: "t16", topic: "我的成长之路", keywords: ["成长", "经历", "变化", "收获", "感悟"] },
  { id: "t17", topic: "谈谈科技发展与社会生活", keywords: ["科技", "发展", "社会", "生活", "影响"] },
  { id: "t18", topic: "我知道的风俗", keywords: ["风俗", "习俗", "传统", "节日", "文化"] },
  { id: "t19", topic: "我和体育", keywords: ["体育", "运动", "锻炼", "健康", "爱好"] },
  { id: "t20", topic: "我的家乡(或熟悉的地方)", keywords: ["家乡", "地方", "记忆", "变化", "情感"] },
  { id: "t21", topic: "谈谈美食", keywords: ["美食", "食物", "烹饪", "餐厅", "味道"] },
  { id: "t22", topic: "我喜欢的节日", keywords: ["节日", "春节", "中秋", "国庆", "生日"] },
  { id: "t23", topic: "我所在的集体(学校、机关、公司等)", keywords: ["集体", "团队", "同事", "合作", "氛围"] },
  { id: "t24", topic: "谈谈社会公德(或职业道德)", keywords: ["公德", "道德", "素质", "责任", "义务"] },
  { id: "t25", topic: "谈谈个人修养", keywords: ["修养", "素质", "品德", "为人", "处世"] },
  { id: "t26", topic: "我喜欢的明星(或其他知名人士)", keywords: ["明星", "偶像", "崇拜", "作品", "品质"] },
  { id: "t27", topic: "我喜爱的书刊", keywords: ["书刊", "阅读", "书籍", "杂志", "内容"] },
  { id: "t28", topic: "谈谈对环境保护的认识", keywords: ["环境", "保护", "污染", "生态", "行动"] },
  { id: "t29", topic: "我向往的地方", keywords: ["向往", "地方", "旅游", "梦想", "目标"] },
  { id: "t30", topic: "购物(消费)的感受", keywords: ["购物", "消费", "体验", "习惯", "观点"] },
];

export default speakingTopics;
