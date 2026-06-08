from pathlib import Path

import streamlit as st

from rag_engine import query_rag


APP_TITLE = "Trợ lý phòng, chống ma túy"
WELCOME = (
    "Xin chào! Tôi có thể giúp bạn tìm hiểu quy định pháp luật, nhận biết nguy cơ "
    "và kiến thức phòng, chống ma túy. Bạn muốn hỏi điều gì?"
)
SUGGESTIONS = [
    "Tàng trữ trái phép chất ma túy bị xử lý thế nào?",
    "Dấu hiệu nhận biết người có nguy cơ sử dụng ma túy?",
    "Gia đình nên làm gì khi phát hiện người thân sử dụng ma túy?",
]


def init_state() -> None:
    if "messages" not in st.session_state:
        reset_chat()


def reset_chat() -> None:
    st.session_state.messages = [
        {"role": "assistant", "content": WELCOME, "sources": []}
    ]


def source_label(source: dict, index: int) -> str:
    raw_name = str(source.get("source", "Không rõ nguồn"))
    name = Path(raw_name).name.replace("_", " ")
    score = source.get("score")
    return f"{index}. {name}" + (f" · {score:.2f}" if isinstance(score, float) else "")


def render_sources(sources: list[dict]) -> None:
    if not sources:
        return
    with st.expander(f"Nguồn tham khảo ({len(sources)})"):
        for index, source in enumerate(sources, 1):
            st.markdown(f"**{source_label(source, index)}**")
            content = str(source.get("content", "")).strip()
            st.caption(content[:700] + ("..." if len(content) > 700 else ""))


def render_message(message: dict) -> None:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])
        render_sources(message.get("sources", []))


def recent_history() -> list[dict]:
    return [
        {"role": item["role"], "content": item["content"]}
        for item in st.session_state.messages[-8:]
    ]


st.set_page_config(page_title=APP_TITLE, page_icon="✦", layout="centered")
st.markdown(
    """
    <style>
    .stApp { background: #ffffff; color: #202123; }
    .block-container { max-width: 850px; padding-top: 1.4rem; padding-bottom: 7rem; }
    [data-testid="stSidebar"] { background: #f7f7f8; border-right: 1px solid #e5e5e5; }
    [data-testid="stChatMessage"] { padding: 1rem 0.25rem; background: transparent; }
    [data-testid="stChatMessageContent"] { font-size: 1rem; line-height: 1.7; }
    [data-testid="stChatInput"] { border-radius: 18px; border-color: #d9d9e3; }
    [data-testid="stExpander"] { border: 1px solid #ececf1; border-radius: 12px; }
    .hero { text-align: center; padding: .5rem 0 1.2rem; }
    .hero h1 { font-size: 1.65rem; margin-bottom: .25rem; }
    .hero p { color: #6b7280; margin: 0; }
    .disclaimer { color: #6b7280; font-size: .78rem; text-align: center; margin-top: 1rem; }
    </style>
    """,
    unsafe_allow_html=True,
)

init_state()

with st.sidebar:
    st.title("Cuộc trò chuyện")
    st.button("＋ Cuộc trò chuyện mới", use_container_width=True, on_click=reset_chat)
    st.divider()
    top_k = st.slider("Số nguồn truy xuất", min_value=2, max_value=8, value=5)
    st.caption(
        "Trợ lý cung cấp thông tin tham khảo từ kho tài liệu. "
        "Không thay thế tư vấn pháp lý hoặc y tế chuyên môn."
    )

st.markdown(
    f'<div class="hero"><h1>{APP_TITLE}</h1>'
    "<p>Hỏi đáp có căn cứ, kèm nguồn tham khảo trực quan</p></div>",
    unsafe_allow_html=True,
)

for chat_message in st.session_state.messages:
    render_message(chat_message)

prompt = st.chat_input("Nhập câu hỏi của bạn...")

if len(st.session_state.messages) == 1:
    st.caption("Gợi ý câu hỏi")
    columns = st.columns(3)
    for column, suggestion in zip(columns, SUGGESTIONS):
        if column.button(suggestion, use_container_width=True):
            prompt = suggestion

if prompt:
    history = recent_history()
    user_message = {"role": "user", "content": prompt, "sources": []}
    st.session_state.messages.append(user_message)
    render_message(user_message)

    with st.chat_message("assistant"):
        with st.spinner("Đang tìm tài liệu và soạn câu trả lời..."):
            result = query_rag(prompt, top_k=top_k, history=history)
        answer = result.get("answer", "Xin lỗi, hệ thống chưa thể trả lời lúc này.")
        sources = result.get("sources", [])
        st.markdown(answer)
        render_sources(sources)

    st.session_state.messages.append(
        {"role": "assistant", "content": answer, "sources": sources}
    )

st.markdown(
    '<p class="disclaimer">Thông tin chỉ mang tính tham khảo. '
    "Trong tình huống khẩn cấp, hãy liên hệ cơ quan chức năng hoặc cơ sở y tế.</p>",
    unsafe_allow_html=True,
)
