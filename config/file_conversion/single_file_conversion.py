import json
import re


def convert_json_to_config(input_file: str, output_file: str) -> None:
    """
    修复核心：自动去除属性值前后空格，避免 gettext 中出现多余空格
    其他规则保持不变：
    1. _key 从 name 动态提取（空格转下划线、大写转小写）
    2. 仅 name/background/connect/connect_method/src/value 带 gettext 包裹
    3. type/panel 不带 gettext
    4. 每个 [menu ...] 块前加空行（首块除外）
    5. 无缩进、属性顺序与目标一致
    """
    # 读取 JSON 输入
    with open(input_file, 'r', encoding='utf-8') as f:
        data = json.load(f)

    output_lines = []
    first_menu_block = True  # 标记是否是第一个 menu 块（首块前不加空行）

    def name_to_key(name: str) -> str:
        """将 name 转换为 menu 路径的 key 格式：大写转小写，空格转下划线"""
        return re.sub(r'\s+', '_', name.strip()).lower()

    def clean_value(value: str) -> str:
        """清除字符串值前后的空格（关键修复：去除多余空格）"""
        if isinstance(value, str):
            return value.strip()  # 去除前后空格，保留中间有效空格
        return value  # 非字符串值直接返回

    def process_node(node: dict, parent_menu_path: list) -> None:
        nonlocal first_menu_block

        # 1. 动态提取当前节点的 key（从 name 属性转换）
        current_name = clean_value(node['name'])  # 确保 name 本身无多余空格
        current_key = name_to_key(current_name)
        current_menu_path = parent_menu_path + [current_key]
        menu_line = f"[menu {' '.join(current_menu_path)}]"

        # 非首块前添加空行
        if not first_menu_block:
            output_lines.append('')
        first_menu_block = False

        output_lines.append(menu_line)

        # 2. 处理节点属性（严格按目标顺序，同时清除值前后空格）
        attr_order = ['name', 'type', 'value', 'connect', 'visible', 'enable', 'method', 'panel','style',
                      'src', 'icon', 'hexpand', 'vexpand', 'position',
                      'button_width', 'button_height', 'v_button_width', 'v_button_height',
                      'column_spacing', 'row_spacing', 'column_homogeneous', 'row_homogeneous',
                      'width', 'height', 'column', 'row', 'columnspan', 'rowspan',
                      'v_width', 'v_height', 'v_column', 'v_row', 'v_columnspan', 'v_rowspan', 'v_column_spacing','v_row_spacing']
        for attr in attr_order:
            if attr not in node:
                continue

            # 清除属性值前后空格（核心修复步骤）
            raw_value = node[attr]
            cleaned_value = clean_value(raw_value)

            # 按规则决定是否用 gettext 包裹（确保无多余空格）
            if attr in ['name', 'background', 'connect', 'src', 'value']:
                # 直接拼接，无额外空格：{{ gettext('xxx') }}
                formatted_value = f" {{{{ gettext('{cleaned_value}') }}}}"
            else:
                formatted_value = cleaned_value

            attr_line = f"{attr}: {formatted_value}"
            output_lines.append(attr_line)

        # 3. 处理子节点（children 字典）
        if 'children' in node and isinstance(node['children'], dict):
            for child_node in node['children'].values():
                process_node(child_node, current_menu_path)

        # 4. 处理直接嵌套的字典属性（如 air_system_HBox）
        for key, value in node.items():
            if key in ['name', 'type', 'value', 'connect', 'visible', 'enable', 'method', 'panel','style',
                      'src', 'icon', 'hexpand', 'vexpand', 'position',
                      'button_width', 'button_height', 'v_button_width', 'v_button_height',
                      'column_spacing', 'row_spacing', 'column_homogeneous', 'row_homogeneous',
                      'width', 'height', 'column', 'row', 'columnspan', 'rowspan',
                      'v_width', 'v_height', 'v_column', 'v_row', 'v_columnspan', 'v_rowspan','v_column_spacing','v_row_spacing']:
                continue
            if isinstance(value, dict) and 'name' in value:
                process_node(value, current_menu_path)

    # 执行递归处理（根节点）
    process_node(data, [])

    # 5. 写入输出文件
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write('\n'.join(output_lines))

    print(f"转换完成！\n输入文件：{input_file}\n输出文件：{output_file}")


if __name__ == "__main__":
    # 配置输入输出文件路径
    name="control_consumables"
    INPUT_FILE = f"HuaFu-json/{name}.json"
    OUTPUT_FILE = f"../{name}.conf"
    convert_json_to_config(INPUT_FILE, OUTPUT_FILE)
