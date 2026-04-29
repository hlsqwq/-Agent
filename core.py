import json
import time
import random
import paho.mqtt.client as mqtt # 用于与底层硬件通信

# ==========================================
# 1. 视觉感知 Agent (Vision Agent)
# ==========================================
class VisionAgent:
    def __init__(self):
        # 实际项目中这里会加载 YOLO 和 SAM/MobileSAM 模型
        print("[Vision Agent] 视觉与分割模型初始化完成...")

    def process_frame(self, frame_data):
        """
        处理摄像头画面，提取场景语义。
        这里使用 Mock 数据模拟模型推理结果。
        """
        # 模拟随机场景：0-人群拥挤, 1-施工路障, 2-道路畅通
        scenario = random.choice(["crowd", "construction", "clear"])
        
        semantics = {
            "timestamp": time.time(),
            "detected_objects": [],
            "scene_context": "",
            "safe_distance_meters": 0.0
        }

        if scenario == "crowd":
            semantics["detected_objects"] = ["person", "person", "bicycle"]
            semantics["scene_context"] = "人群密集，移动缓慢"
            semantics["safe_distance_meters"] = 1.2
        elif scenario == "construction":
            semantics["detected_objects"] = ["traffic_cone", "excavator"]
            semantics["scene_context"] = "前方固定施工区域，主路阻断"
            semantics["safe_distance_meters"] = 3.5
        else:
            semantics["detected_objects"] = []
            semantics["scene_context"] = "道路畅通"
            semantics["safe_distance_meters"] = 10.0

        print(f"[Vision Agent] 画面解析完毕: {semantics['scene_context']}")
        return semantics


# ==========================================
# 2. 逻辑推理 Agent (Reasoning Agent)
# ==========================================
class ReasoningAgent:
    def __init__(self):
        print("[Reasoning Agent] 长链推理引擎初始化完成...")

    def execute_reasoning_chain(self, vision_context, destination):
        """
        结合视觉上下文和目的地进行逻辑推理。
        实际项目中可接入本地部署的大模型（如 Qwen/Llama）或调用云端 API。
        """
        print(f"[Reasoning Agent] 正在分析当前态势... 目的地: {destination}")
        
        objects = vision_context["detected_objects"]
        context = vision_context["scene_context"]
        
        decision = {
            "strategy": "",
            "reasoning_log": "",
            "target_speed": 0.0,
            "steering": 0.0 # -1.0 到 1.0
        }

        # 模拟 LLM 的长链推理逻辑
        if "人群密集" in context:
            decision["strategy"] = "WAIT"
            decision["reasoning_log"] = "检测到前方人群密集，分析当前为下课高峰期，强行穿插风险高，最优策略为原地等待人群散去。"
            decision["target_speed"] = 0.0
            
        elif "施工区域" in context:
            decision["strategy"] = "REROUTE"
            decision["reasoning_log"] = "检测到固定路障和施工车辆，原直线路径失效。需启动网格绕行算法，向左侧草坪边缘重新规划路径。"
            decision["target_speed"] = 0.5
            decision["steering"] = -0.8 # 向左转
            
        else:
            decision["strategy"] = "PROCEED"
            decision["reasoning_log"] = "未检测到动态障碍物，视野开阔，按照规划路径全速前进。"
            decision["target_speed"] = 2.0
            decision["steering"] = 0.0
            
        print(f"[Reasoning Agent] 推理完成: {decision['reasoning_log']}")
        return decision


# ==========================================
# 3. 底层控制 Agent (Control Agent)
# ==========================================
class ControlAgent:
    def __init__(self, broker_address="localhost", port=1883):
        self.client = mqtt.Client(client_id="Gateway_Control_Agent")
        # 实际环境应开启以下连接代码：
        # self.client.connect(broker_address, port, 60)
        # self.client.loop_start()
        print("[Control Agent] 控制节点初始化，MQTT 通信就绪...")

    def dispatch_command(self, decision):
        """
        将高级策略转化为底层硬件能识别的控制指令（如电机 PWM 占空比、舵机角度）。
        """
        cmd_payload = {
            "cmd_type": "DRIVE",
            "speed_m_s": decision["target_speed"],
            "steer_angle": decision["steering"],
            "timestamp": int(time.time() * 1000)
        }
        
        # 将指令通过 MQTT 发送给底盘硬件
        # self.client.publish("robot/hardware/cmd", json.dumps(cmd_payload))
        
        print(f"[Control Agent] 已下发底层指令 -> 速度: {cmd_payload['speed_m_s']}m/s, 转向: {cmd_payload['steer_angle']}")
        print("-" * 50)


# ==========================================
# 4. 主系统调度器 (Coordinator)
# ==========================================
def main_loop():
    print("=== 园区自动化配送 Agent 系统启动 ===\n")
    
    vision_agent = VisionAgent()
    reasoning_agent = ReasoningAgent()
    control_agent = ControlAgent()
    
    destination = "图书馆快递柜"
    
    # 模拟系统的运行循环 (Tick)
    try:
        for tick in range(1, 4):
            print(f"\n>>> [系统时钟] Tick: {tick}")
            
            # 1. 感知：获取并处理摄像头帧
            camera_frame = b"mock_image_bytes" 
            vision_data = vision_agent.process_frame(camera_frame)
            
            # 2. 决策：长链推理
            decision = reasoning_agent.execute_reasoning_chain(vision_data, destination)
            
            # 3. 控制：指令下发
            control_agent.dispatch_command(decision)
            
            time.sleep(2) # 模拟处理间隔
            
    except KeyboardInterrupt:
        print("\n系统手动停止。")

if __name__ == "__main__":
    main_loop()