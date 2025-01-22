module.exports = {
  content: [
    "./templates/**/*.html", // 掃描模板目錄中的 HTML 文件
    "./**/templates/**/*.html", // 掃描應用目錄中的模板
    "./static/**/*.js", // 掃描靜態 JS 文件
  ],
  theme: {
    extend: {},
  },
  plugins: [],
};
