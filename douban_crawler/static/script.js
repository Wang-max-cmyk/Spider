document.addEventListener("DOMContentLoaded", () => {
  const crawlForm = document.getElementById("crawlForm")
  const submitBtn = document.getElementById("submitBtn")
  const resultSection = document.getElementById("resultSection")
  const loading = document.getElementById("loading")
  const results = document.getElementById("results")
  const sentimentChart = document.getElementById("sentimentChart")
  const wordcloudChart = document.getElementById("wordcloudChart")
  const downloadSentiment = document.getElementById("downloadSentiment")
  const downloadWordcloud = document.getElementById("downloadWordcloud")
  const downloadCsv = document.getElementById("downloadCsv")
  const downloadJson = document.getElementById("downloadJson")

  // 当前任务ID
  let currentTaskId = null

  // 表单提交处理
  crawlForm.addEventListener("submit", (e) => {
    e.preventDefault()

    // 获取表单数据
    const formData = new FormData(crawlForm)
    const type = formData.get("type")
    const name = formData.get("name")
    const count = formData.get("count")
    const status = formData.get("status")

    // 禁用提交按钮
    submitBtn.disabled = true
    submitBtn.textContent = "处理中..."

    // 显示加载区域
    resultSection.style.display = "block"
    loading.style.display = "block"
    results.style.display = "none"

    // 发送爬取请求
    fetch("/api/crawl", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({
        type: type,
        name: name,
        count: Number.parseInt(count),
        status: status,
      }),
    })
      .then((response) => response.json())
      .then((data) => {
        if (data.code === 1) {
          // 保存任务ID
          currentTaskId = data.task_id

          // 开始轮询任务状态
          checkTaskStatus(currentTaskId)
        } else {
          // 显示错误
          alert("爬取失败: " + data.msg)
          resetForm()
        }
      })
      .catch((error) => {
        console.error("Error:", error)
        alert("请求出错，请重试")
        resetForm()
      })
  })

  // 显示结果
  function displayResults(data) {
    // 隐藏加载区域，显示结果区域
    loading.style.display = "none"
    results.style.display = "block"

    // 设置图片源
    sentimentChart.src = `/api/image/${data.sentiment_chart}?t=${Date.now()}`
    // 这里加上时间戳，避免浏览器缓存
    wordcloudChart.src = `/api/image/${data.wordcloud_chart}?t=${Date.now()}`

    // 设置下载链接
    downloadSentiment.href = `/api/download/${data.sentiment_chart}`
    downloadSentiment.download = data.sentiment_chart

    downloadWordcloud.href = `/api/download/${data.wordcloud_chart}`
    downloadWordcloud.download = data.wordcloud_chart

    downloadCsv.href = `/api/download/${data.csv_file}`
    downloadCsv.download = data.csv_file

    downloadJson.href = `/api/download/${data.json_file}`
    downloadJson.download = data.json_file

    // 重置表单状状态
    submitBtn.disabled = false
    submitBtn.textContent = "开始爬取"
  }

  // 重置表单状态
  function resetForm() {
    submitBtn.disabled = false
    submitBtn.textContent = "开始爬取"
    resultSection.style.display = "none"
  }
})
