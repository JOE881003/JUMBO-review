import random
from dataclasses import dataclass
import streamlit as st

# =========================
# 抽獎邏輯區
# =========================

# 玩家狀態
@dataclass
class GachaState:
    total_draws: int = 0   # 總抽獎次數
    total_wins: int = 0    # 總得獎次數（頭獎+二獎）
    lose_count: int = 0    # 目前連續沒中獎次數
    just_won: bool = False # 是否剛中獎

# 固定基礎機率
P1 = 0.05  # 頭獎機率
P2 = 0.10  # 二獎機率

# 保底判斷
def is_guarantee(state: GachaState) -> bool:
    # 新玩家：前 4 抽都沒中 → 第 5 抽保底
    new_player = (state.total_draws == 4 and state.total_wins == 0)
    # 連續 19 抽沒中 → 第 20 抽保底
    lose_19 = (state.lose_count == 19)
    return new_player or lose_19

# 動態倍率
def factor(state: GachaState) -> float:
    if state.just_won:
        return 0.8
    elif 0 <= state.lose_count <= 3:
        return 1.0
    elif 4 <= state.lose_count <= 10:
        return 1.05
    return 1.10

# 執行一次抽獎
def draw(state: GachaState, rn=random.random):
    # 1. 先檢查保底
    if is_guarantee(state):
        state.total_draws += 1
        state.just_won = True
        state.lose_count = 0

        r = rn()
        if r < 1/3:
            result = "top"
        else:
            result = "second"

        state.total_wins += 1
        return result, state

    # 2. 一般抽獎
    f = factor(state)
    P1_f = P1 * f
    P2_f = P2 * f

    # 確保總機率不超過 1，保持比例
    total = P1_f + P2_f
    if total > 1:
        P1_f /= total
        P2_f /= total

    r = rn()
    state.total_draws += 1

    if r < P1_f:
        result = "top"
        state.total_wins += 1
        state.just_won = True
        state.lose_count = 0
    elif r < P1_f + P2_f:
        result = "second"
        state.total_wins += 1
        state.just_won = True
        state.lose_count = 0
    else:
        result = "none"
        state.just_won = False
        state.lose_count += 1

    return result, state


# 大量模擬
def simulate(
    num_player: int = 5000,
    draws_per_player: int = 100,
    price_per_draw: int = 50,
    top_pay: int = 60,
    second_pay: int = 20,
):
    """
    num_player: 玩家數
    draws_per_player: 每個玩家抽幾次
    price_per_draw: 每抽花多少錢
    top_pay: 頭獎金額
    second_pay: 二獎金額
    """

    total_draws = 0
    top_count = 0
    second_count = 0
    none_count = 0

    total_pay = 0           # 玩家總拿到獎金
    max_lose_lst = []       # 每名玩家最大連敗數

    for _ in range(num_player):
        state = GachaState()   # 每位玩家有自己的 state
        player_max_lose = 0

        for _ in range(draws_per_player):
            result, state = draw(state)
            total_draws += 1

            if result == "top":
                top_count += 1
                total_pay += top_pay
            elif result == "second":
                second_count += 1
                total_pay += second_pay
            else:
                none_count += 1

            player_max_lose = max(player_max_lose, state.lose_count)

        max_lose_lst.append(player_max_lose)

    top_prop = top_count / total_draws if total_draws > 0 else 0
    second_prop = second_count / total_draws if total_draws > 0 else 0
    avg_max_lose = sum(max_lose_lst) / len(max_lose_lst) if max_lose_lst else 0

    avg_pay = total_pay / total_draws if total_draws > 0 else 0
    avg_income = price_per_draw - avg_pay

    result = {
        "total_draws": total_draws,
        "top_count": top_count,
        "second_count": second_count,
        "none_count": none_count,
        "top_prop": top_prop,
        "second_prop": second_prop,
        "avg_max_lose": avg_max_lose,
        "avg_pay": avg_pay,
        "avg_income": avg_income
    }
    return result


# =========================
# Streamlit 介面區
# =========================

st.set_page_config(page_title="抽獎機率模擬器", layout="centered")

st.title(" JUMBO 初審題")

st.set_page_config(page_title="抽獎機率模擬器", layout="centered")

# ------------ 左側選單 ------------
page = st.sidebar.radio(
    "選擇頁面",
    [
        "題目一: 抽獎遊戲",
        "題目二：衛生紙",
        "題目三：紙筆硬幣遊戲",
    ]
)

# =========================
# 頁面一：抽獎遊戲（原本的兩個 tab）
# =========================
if page == "題目一: 抽獎遊戲":
    st.title("抽獎機率設計 Demo")

    tab1, tab2 = st.tabs(["即時抽獎", "大量模擬"])

    # ---------- Tab 1：即時抽獎 ----------
    with tab1:
        st.header("即時抽獎")

        # 初始化 session state
        if "gacha_state" not in st.session_state:
            st.session_state["gacha_state"] = GachaState()
        if "last_result" not in st.session_state:
            st.session_state["last_result"] = None

        state: GachaState = st.session_state["gacha_state"]

        col1, col2 = st.columns(2)
        with col1:
            if st.button("🎲 抽一次"):
                res, new_state = draw(state)
                st.session_state["gacha_state"] = new_state
                st.session_state["last_result"] = res
        with col2:
            if st.button("🔁 重置玩家狀態"):
                st.session_state["gacha_state"] = GachaState()
                st.session_state["last_result"] = None
                st.success("已重置玩家狀態！")

        # 顯示抽獎結果
        last_res = st.session_state["last_result"]
        st.subheader("本次抽獎結果")

        if last_res == "top":
            st.success("大獎 🎉🎉")
        elif last_res == "second":
            st.info("貳獎！")
        elif last_res == "none":
            st.warning("😢 這次沒有中獎")
        else:
            st.write("按上面的「🎲 抽一次」")

        st.subheader("目前玩家狀態")
        c1, c2, c3, c4 = st.columns(4)
        c1.metric("總抽獎次數", state.total_draws)
        c2.metric("總得獎次數", state.total_wins)
        c3.metric("目前連續沒中獎", state.lose_count)
        c4.metric("上一抽是否中獎", "是" if state.just_won else "否")
        st.markdown("---")
        st.subheader("抽獎機率流程圖")

        st.image(
            "image/JUMBO.drawio.png",
            caption="抽獎規則流程圖（保底 + 動態倍率邏輯）",
            use_container_width=True
        )

    # ---------- Tab 2：大量模擬 ----------
    with tab2:
        st.header("大量模擬結果")

        st.write("這裡可以一次模擬多名玩家，查看整體機率、平均獲利、連敗狀況。")

        with st.form("sim_form"):
            col1, col2 = st.columns(2)
            with col1:
                num_player = st.number_input("玩家數", min_value=100, max_value=100000, value=5000, step=100)
                draws_per_player = st.number_input("每位玩家抽幾次", min_value=10, max_value=500, value=100, step=10)
            with col2:
                top_pay = st.number_input("頭獎金額", min_value=1, max_value=2000, value=60, step=10)
                second_pay = st.number_input("二獎金額", min_value=1, max_value=2000, value=20, step=5)

            price_per_draw = st.number_input("每抽花費（玩家支付）", min_value=1, max_value=200, value=50, step=5)

            submitted = st.form_submit_button("開始模擬")

        if submitted:
            sim = simulate(
                num_player=int(num_player),
                draws_per_player=int(draws_per_player),
                price_per_draw=int(price_per_draw),
                top_pay=int(top_pay),
                second_pay=int(second_pay),
            )

            st.subheader("模擬結果")
            st.write(f"總抽獎次數：**{sim['total_draws']}**")
            st.write(f"- 頭獎次數：**{sim['top_count']}**（約 {sim['top_prop']*100:.2f}%）")
            st.write(f"- 二獎次數：**{sim['second_count']}**（約 {sim['second_prop']*100:.2f}%）")
            st.write(f"- 未中獎次數：**{sim['none_count']}**")

            st.write("---")
            st.write(f"每位玩家「最大連續沒中獎」的平均值：約 **{sim['avg_max_lose']:.2f} 抽**")
            st.write("---")
            st.write(f"每抽平均發出去的獎金：約 **{sim['avg_pay']:.2f} 元**")
            st.write(f"每抽平均利潤：約 **{sim['avg_income']:.2f} 元**（每抽收 {price_per_draw} 元）")


# =========================
# 頁面二：題目二 衛生紙
# =========================
elif page == "題目二：衛生紙":
    st.title("題目二：物品特性說明（衛生紙）")

    st.markdown("""
**物品：衛生紙**

1. **材質：柔軟的紙纖維**  
   - 摸起來軟軟的。  
   - 具有良好的吸水力，可以快速吸收水分。  
   - 厚度適中，不容易一擦就破。

2. **結構：多層薄紙壓在一起**  
   - 一般衛生紙有 2～3 層。  
   - 折疊與堆疊方式設計成抽取式時，可以讓下一張衛生紙被帶出，方便連續使用。

3. **用途**  
   - 吸水、擦水，例如擦手、擦汗、擦灑出的飲料。  
   - 上廁所後的清潔。  
    """)

# =========================
# 頁面三：題目三 遊戲設計
# =========================
elif page == "題目三：紙筆硬幣遊戲":
    st.title("題目三：紙筆硬幣遊戲設計")

    st.markdown("""
這個遊戲需要 **紙、筆、一枚硬幣，和至少一名朋友**。  
首先在紙上畫一個 **5×5 的格子**，形成一張簡單的地圖。接著把紙翻到背面，請朋友在相對應的位置隨機圈出五個寶藏的位置，玩家不能偷看。完成後再翻回正面，由玩家在任意一格選一個起始位置，把硬幣放上去，代表自己的角色。

遊戲開始後，每一回合玩家都要丟一次硬幣：

- 若丟到 **正面**：可以把硬幣往上、下、左、右其中一個方向移動一格。  
- 若丟到 **反面**：表示前方受阻，玩家必須在任意一格畫上一個叉叉，代表那一格之後不能再走進去。

遊戲進行 **12 回合** 後結束，這時翻到紙的背面對答案：  
若玩家的移動路徑中，有經過朋友事先圈起來的寶藏格子，每找到一個寶藏就加一分。每位朋友輪流當玩家，各自玩一輪，最後比較分數，高分者獲勝。
    """)
