# -*- coding:utf-8 -*-
import re


class TempliteSyntaxError(ValueError):
    pass


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


class Templite:
    def __init__(self, text, *contexts):
        """
        text:是输入的模板

        contexts:是输入的数据与过滤器函数
        """
        self.context = {}
        for context in contexts:
            self.context.update(context)

        # 所有的变量名
        self.all_vars = set()
        # 属于循环的变量名
        self.loop_vars = set()

        code = CodeBuilder()

        code.add_line('def render_function(context, do_dots):')
        code.indent()
        # 先加个section占位, 从上下文提取变量的代码在之后实现
        vars_code = code.add_section()
        code.add_line('result = []')
        code.add_line('append_result = result.append')
        code.add_line('extend_result = result.extend')
        code.add_line('to_str = str')

        buffered = []
        def flush_output():
            # 如果追加的代码只有一个使用append
            if len(buffered) == 1:
                code.add_line('append_result({0})'.format(buffered[0]))
            # 其余则使用extend
            elif len(buffered) > 1:
                code.add_line('extend_result([{0}])'.format(','.join(buffered)))
            # 清空缓存
            del buffered[:]

        ops_stack = []

        tokens = re.split(r'(?s)({{.*?}}|{%.*?%}|{#.*?#})', text)
        for token in tokens:
            if token.startswith('{#'):
                continue
            elif token.startswith('{{'):
                # 得到python表达式
                expr = self._expr_code(token[2:-2].strip())
                buffered.append('to_str({0})'.format(expr))
            elif token.startswith('{%'):
                flush_output()
                words = token[2:-2].strip().split()
                if words[0] == 'if':
                    if len(words) != 2:
                        self._syntax_error("Don't understand if", token)
                    ops_stack.append('if')
                    code.add_line('if {0}:'.format(self._expr_code(words[1])))
                    code.indent()
                elif words[0] == 'for':
                    if len(words) != 4 or words[2] != 'in':
                        self._syntax_error("Don't understand for", token)
                    ops_stack.append('for')
                    self._variable(words[1], self.loop_vars)
                    code.add_line('for c_{0} in {1}:'.\
                                  format(words[1], self._expr_code(words[3])))
                    code.indent()
                elif words[0].startswith('end'):
                    if len(words) != 1:
                        self._syntax_error("Don't understand end", token)
                    end_what = words[0][3:]
                    if not ops_stack:
                        self._syntax_error('Too many ends', token)
                    start_what = ops_stack.pop()
                    if end_what != start_what:
                        self._syntax_error('Mismatched end tag', end_what)
                    code.dedent()
                else:
                    self._syntax_error("Don't understand tag", words[0])
            else:
                if token:
                    buffered.append(repr(token))

        if ops_stack:
            self._syntax_error("Unmatched action tag", ops_stack[-1])
        flush_output()

        for var_name in self.all_vars - self.loop_vars:
            vars_code.add_line('c_{0} = context[{1!r}]'.format(var_name, var_name))
        code.add_line("return ''.join(result)")
        code.dedent()

        self._render_function = code.get_globals()['render_function']
        print(code)

    def _expr_code(self, expr):
        """根据expr生成python表达式"""
        if '|' in expr:
            pipes = expr.split('|')
            code = self._expr_code(pipes[0])
            for func in pipes[1:]:
                self._variable(func, self.all_vars)
                code = 'c_{0}({1})'.format(func, code)
        elif '.' in expr:
            dots = expr.split('.')
            code = self._expr_code(dots[0])
            args = ', '.join(repr(d) for d in dots[1:])
            code = 'do_dots({0}, {1})'.format(code, args)
        else:
            self._variable(expr, self.all_vars)
            code = 'c_{0}'.format(expr)
        return code

    def _syntax_error(self, msg, thing):
        """抛出一个语法错误"""
        raise TempliteSyntaxError('{0}: {1!r}'.format(msg, thing))

    def _variable(self, name, vars_set):
        """将变量存入指定的变量集中,同时验证变量名的有效性"""
        if not re.match('[_a-zA-Z][_a-zA-Z0-9]', name):
            self._syntax_error("Not a valid name", name)
        vars_set.add(name)

    def render(self, context=None):
        render_context = dict(self.context)
        if context:
            render_context.update(context)
        return self._render_function(render_context, self._do_dots)

    def _do_dots(self, value, *dots):
        for dot in dots:
            try:
                value = getattr(value, dot)
            except AttributeError:
                value = value[dot]
            if callable(value):
                value = value()
        return value


