# -*- coding:utf-8 -*-
import re


# 创建Templite对象
templite = Templite('''
    <h1>Hello {{name|upper}}!</h1>
    {% for topic in topics %}
        <p>You are interested in {{topic}}.</p>
    {% endfor %}
    ''',
    {'upper': str.upper},
)

# 稍后调用render导入数据
text = templite.render({
    'name': "Ned",
    'topics': ['Python', 'Geometry', 'Juggling'],
})


class CodeBuilder:
    INDENT_STEP = 4

    def __init__(self, indent=0):
        self.code = []
        self.indent_level = indent

    def add_line(self, line):
        self.code.extend([' ' * self.indent_level, line, '\n'])

    def indent(self):
        """增加一级缩进"""
        self.indent_level += self.INDENT_STEP

    def dedent(self):
        """缩小一级缩进"""
        self.indent_level -= self.INDENT_STEP

    def add_section(self):
        section = CodeBuilder(self.indent_level)
        self.code.append(section)
        return section

    def __str__(self):
        return ''.join(str(c) for c in self.code)

    def get_globals(self):
        """运行代码并返回名字空间字典"""
        # 检查缩进, 保证所有块(block)都已经处理完
        assert self.indent_level == 0
        # 得到生成的代码
        python_source = str(self)
        # 运行代码后得到的名字空间
        global_namespace = {}
        # 如果没有local_namespace参数,则global_namepace会同时包含局部和全局的变量
        exec(python_source, global_namespace)
        return global_namespace