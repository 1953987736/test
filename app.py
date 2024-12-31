import requests
from bs4 import BeautifulSoup
import re
import jieba
from collections import Counter
from pyecharts import options as opts
from pyecharts.charts import WordCloud, Bar, Pie, Line, Scatter, Funnel, Radar
import streamlit as st


def outCome():
    if url:
        try:
            # 请求网页
            response = requests.get(url)
            response.raise_for_status()  # 检查请求是否成功
            soup = BeautifulSoup(response.text, 'html.parser')

            # 提取body标签内的所有文本
            body_tag = soup.find('body')
            if body_tag:
                content = body_tag.get_text()

                clean_text = re.sub(r'<[^>]+>', '', content)  # 去除HTML标签
                clean_text = re.sub(r'[^\w\s]', '', clean_text)  # 去除标点符号
                clean_text = re.sub(r'\s+', ' ', clean_text).strip()  # 去除多余的空格和空白字符

                # 分词
                words = jieba.lcut(clean_text)

                # 过滤掉空字符串
                words = [word for word in words if word.strip()]

                # 统计词频
                word_counts = Counter(words)

                # 获取词频最高的20个词
                top_20_words = word_counts.most_common(20)

                # 显示词频排名前20的词汇
                st.write("词频排名前20的词汇:")
                for word, count in top_20_words:
                    st.write(f"{word}: {count}")

                # 根据选择显示不同类型的图表
                if op == "词云图":
                    wordcloud = (
                        WordCloud()
                       .add("", [list(t) for t in word_counts.items()], shape="circle")
                       .set_global_opts(title_opts=opts.TitleOpts(title="词云图"))
                    )
                    chart = wordcloud
                elif op == "条形图":
                    bar = (
                        Bar()
                       .add_xaxis([w[0] for w in top_20_words])
                       .add_yaxis("频率", [w[1] for w in top_20_words])
                       .set_global_opts(title_opts=opts.TitleOpts(title="条形图"))
                    )
                    chart = bar
                elif op == "饼图":
                    pie = (
                        Pie()
                       .add("", [list(w) for w in top_20_words])
                       .set_global_opts(title_opts=opts.TitleOpts(title="饼图"))
                    )
                    chart = pie
                elif op == "折线图":
                    line = (
                        Line()
                       .add_xaxis([w[0] for w in top_20_words])
                       .add_yaxis("频率", [w[1] for w in top_20_words])
                       .set_global_opts(title_opts=opts.TitleOpts(title="折线图"))
                    )
                    chart = line
                elif op == "散点图":
                    scatter = (
                        Scatter()
                       .add_xaxis([w[0] for w in top_20_words])
                       .add_yaxis("频率", [w[1] for w in top_20_words])
                       .set_global_opts(title_opts=opts.TitleOpts(title="散点图"))
                    )
                    chart = scatter
                elif op == "雷达图":
                    radar = (
                        Radar()
                       .add_schema([opts.RadarIndicatorItem(name=w[0], max_=max([w[1] for w in top_20_words]))for w in top_20_words])
                       .add("词频", [[w[1] for w in top_20_words]], color="blue")
                       .set_global_opts(title_opts=opts.TitleOpts(title="雷达图"))
                    )
                    chart = radar
                elif op == "漏斗图":
                    funnel = (
                        Funnel()
                       .add("", [list(w) for w in top_20_words])
                       .set_global_opts(title_opts=opts.TitleOpts(title="漏斗图"))
                    )
                    chart = funnel

                # 生成并显示图表
                chart_html = chart.render_embed()
                st.components.v1.html(chart_html, height=500)

                # 交互过滤低频词
                filtered_words = {k: v for k, v in word_counts.items() if v >= min_freq}
                st.write("过滤后的词汇表:")
                for word, count in sorted(filtered_words.items(), key=lambda x: x[1], reverse=True):
                    st.write(f"{word}: {count}")
            else:
                st.error("未找到body标签")
        except requests.exceptions.RequestException as e:
            st.error(f"无法访问该URL，请检查网络或URL是否正确。错误信息: {e}")


# Streamlit界面设置
st.title("交互式文本分析Web应用")
st.sidebar.header("选项")
# 选择图表类型
op = st.sidebar.selectbox(
    "请选择图表类型",
    ["词云图", "条形图", "饼图", "折线图", "散点图", "雷达图", "漏斗图"]  # 选项中修改为雷达图
)
# 选择最低词频
min_freq = st.sidebar.slider("选择最低词频", 1, 100, 1)  # 假设最大词频为100，可以根据实际情况调整
# 用户输入URL
url = st.text_input("请输入文章URL:", "")
outCome()  # 调用函数以显示结果