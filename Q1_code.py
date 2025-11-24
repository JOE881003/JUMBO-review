import random
from dataclasses import dataclass

#-----設定玩家目前抽獎狀態-----
@dataclass
class GachaState:
    total_draws: int = 0 #總抽獎次數
    total_wins: int = 0 #總得獎次數
    lose_count: int = 0 #目前連續沒中獎次數
    just_won: bool = False #是否剛中獎

#-----中大獎與貳獎機率-----
P1 = 0.05 #頭獎機率
P2 = 0.1 #二獎機率

#-----設定保底-----
def is_guarantee (state: GachaState):
    new_player = (state.total_draws == 4 and state.total_wins == 0) #新玩家前五次必保底
    lose_19 = (state.lose_count == 19) #連續抽19抽沒中下一抽必保底
    return new_player or lose_19 #回傳是否因保底中獎

#-----動態倍率-----
def factor(state: GachaState):
    
    if state.just_won: #如果剛中過獎則動態倍率調低使中獎機率稍微降低
        return 0.8
    elif 0 <= state.lose_count <= 3: #連敗 1 到 3 次倍率條回正常
        return 1
    elif 4 <= state.lose_count <= 10: #連敗 4 到 10 次倍率提高中獎機率提高
        return 1.05
    
    return 1.10 #連敗 10 次以上倍率再次提高

#-----執行抽獎-----


def draw(state:GachaState, rn = random.random):
    
    #1. 檢查保底
    if is_guarantee(state) == True:
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
    
    #2. 一般抽獎
    f = factor(state)
    P1_f = P1 * f
    P2_f = P2 * f
    
    P1_f = min(P1, 1)
    P2_f = min(P2, 1)
    
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
        
        
def simulate(
    num_player = 5000,
    draws_per_player = 100,
    price_per_draw = 50,
    top_pay = 60,
    second_pay = 20,
):
    """
    num_player: 玩家數
    draws_per_player: 每個玩家抽幾次 ( 20 到 150 隨機取)
    price_per_draw: 每抽花多少錢
    jackpot_prize: 頭獎金額
    second_prize: 二獎金額
    """       
    draws_per_player = random.randint(20, 150)
    total_draws = 0
    top_count = 0
    second_count = 0
    none_count = 0
    
    total_pay = 0 #玩家拿到的獎金
    max_lose_lst = [] #每名玩家最大連敗數
    
    for _ in range(num_player): #遍歷每個玩家
        state = GachaState()
        player_max_lose = 0
        for _ in range (draws_per_player): #遍歷每個玩家遊玩次數
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


    top_prop = top_count / total_draws #抽到大獎的機率
    second_prop = second_count / total_draws #抽到二獎的機率
    
    avg_max_lose = sum(max_lose_lst) / len(max_lose_lst)# 平均最大連續失敗次數


    avg_pay = total_pay / total_draws #每抽的平均獎金
    avg_income = price_per_draw - avg_pay #每抽的公司的平均收益

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


if __name__ == "__main__":
    # 這裡你可以自己調頭獎／二獎金額
    JACKPOT_PRIZE = 60   # 頭獎
    SECOND_PRIZE = 20    # 二獎

    sim = simulate(
        num_player=5000,
        draws_per_player=100,
        price_per_draw=50,
        top_pay=JACKPOT_PRIZE,
        second_pay=SECOND_PRIZE,
    )



print("===== 抽獎模擬結果 =====")
print(f"總抽獎次數         : {sim['total_draws']}")
print(f"頭獎次數           : {sim['top_count']}  (約 {sim['top_prop']*100:.2f}%)")
print(f"二獎次數           : {sim['second_count']}  (約 {sim['second_prop']*100:.2f}%)")
print(f"未中獎次數         : {sim['none_count']}")
print()
print(f"每位玩家最大連敗次數 平均 : {sim['avg_max_lose']:.2f}")
print(f"每抽平均發出去的獎金 : {sim['avg_pay']:.2f} 元")
print(f"每抽公司平均淨利潤   : {sim['avg_income']:.2f} 元 (抽一次收 50 元)")
print("=======================")





