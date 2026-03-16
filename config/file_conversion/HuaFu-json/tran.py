import json
import os
from collections import OrderedDict
from pathlib import Path


def batch_convert_calibration_json():
    """
    批量转换JSON文件：
    - 脚本位置：a文件夹下
    - 原文件：a文件夹下的所有.json文件
    - 输出文件：同级的b文件夹（自动创建），保持原文件名不变
    """
    # ========== 路径配置（根据你的场景固定） ==========
    # 脚本所在目录（a文件夹）
    script_dir = Path(__file__).parent.absolute()
    # 输入目录 = a文件夹
    input_dir = script_dir
    # 输出目录 = a文件夹同级的b文件夹
    output_dir = script_dir.parent / "b"

    # 自动创建b文件夹（不存在则创建）
    output_dir.mkdir(parents=True, exist_ok=True)

    # ========== 核心：固定键顺序（无h_相关） ==========
    FIXED_KEY_ORDER = [
        'father',
        'name',
        'type',
        'value',
        'connect',
        'visible',
        'enable',
        'method',
        'panel'
        'style',
        'src',
        'icon',
        'hexpand',
        'vexpand',
        'position',
        'button_width',
        'button_height',
        'v_button_width',
        'v_button_height',
        'column_spacing',
        'row_spacing',
        'column_homogeneous',
        'row_homogeneous',
        'width',
        'height',
        'column',
        'row',
        'columnspan',
        'rowspan',
        'v_width',
        'v_height',
        'v_column',
        'v_row',
        'v_columnspan',
        'v_rowspan',
        'children'
    ]

    # 定义需要添加 v_ 前缀的字段列表
    prefix_fields = [
        "column", "row", "columnspan", "rowspan",
        "width", "height", "button_width", "button_height"
    ]

    # 单个文件的处理逻辑
    def process_single_file(file_path):
        # 读取原始 JSON 文件
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                data = json.load(f)
        except Exception as e:
            print(f"❌ 读取文件 {file_path.name} 失败：{str(e)}")
            return False

        # 递归处理字段：仅生成v_字段 + 保留原字段 + 按固定顺序排序
        def process_node(node):
            if isinstance(node, dict):
                # 生成v_前缀字段（保留原字段）
                v_fields = {}
                keys = list(node.keys())
                for key in keys:
                    if key in prefix_fields and key in node:
                        v_fields[f"v_{key}"] = node[key]
                node.update(v_fields)

                # 按固定顺序重新排列
                ordered_node = OrderedDict()
                for key in FIXED_KEY_ORDER:
                    if key in node:
                        if key == "children":
                            process_node(node[key])
                        ordered_node[key] = node[key]
                # 处理额外键
                for key in node.keys():
                    if key not in FIXED_KEY_ORDER and key not in ordered_node:
                        ordered_node[key] = node[key]

                # 递归处理子节点
                for key, value in ordered_node.items():
                    if key != "children" and isinstance(value, (dict, list)):
                        process_node(value)

                # 替换为有序字典
                node.clear()
                node.update(ordered_node)

            elif isinstance(node, list):
                for item in node:
                    process_node(item)

        # 处理当前文件数据
        process_node(data)

        # 生成输出文件路径（b文件夹下，保持原文件名）
        output_file_path = output_dir / file_path.name

        # 写入转换后的文件
        try:
            class OrderedJsonEncoder(json.JSONEncoder):
                def default(self, obj):
                    if isinstance(obj, OrderedDict):
                        return dict(obj)
                    return super().default(obj)

            with open(output_file_path, "w", encoding="utf-8") as f:
                json.dump(data, f, cls=OrderedJsonEncoder, indent=2, ensure_ascii=False)

            print(f"✅ 成功：{file_path.name} → b/{file_path.name}")
            return True
        except Exception as e:
            print(f"❌ 写入文件 {file_path.name} 失败：{str(e)}")
            return False

    # ========== 批量遍历a文件夹下的.json文件 ==========
    # 只遍历a文件夹（脚本所在目录）下的.json文件（不递归子文件夹）
    file_list = list(input_dir.glob("*.json"))
    # 排除脚本自身（如果脚本是.py文件，无需排除，此处做兜底）
    file_list = [f for f in file_list if f.suffix.lower() == ".json"]

    if not file_list:
        print(f"⚠️ 警告：在a文件夹（{input_dir}）中未找到.json文件")
        return

    print(f"\n📁 开始批量转换，共找到 {len(file_list)} 个JSON文件：")
    success_count = 0
    for file in file_list:
        if process_single_file(file):
            success_count += 1

    # 输出汇总信息
    print(f"\n📊 转换完成！成功：{success_count} 个，失败：{len(file_list) - success_count} 个")
    print(f"📌 输出路径：{output_dir.absolute()}")


# ========== 直接运行即可 ==========
if __name__ == "__main__":
    batch_convert_calibration_json()
