#!/usr/bin/python3
# coding: utf-8

import sys, re
from handlers import *
from util import *
from rules import *


class Parser:
    '''
    解析器父类
    '''
    def __init__(self, handler):
        self.handler = handler
        self.rules = []
        self.filters = []

    def add_rule(self, rule):
        # 添加规则
        self.rules.append(rule)

    def add_filter(self, pattern, name):
        # 添加过滤器
        def filter(block, handler):
            return re.sub(pattern, handler.sub(name), block)
        self.filters.append(filter)

    def parse(self, file):
        # 解析
        self.handler.start('document')
        for block in blocks(file):
            for filter in self.filters:
                block = filter(block, self.handler)
            for rule in self.rules:
                if rule.condition(block):
                    last = rule.action(block, self.handler)
                    if last: break
        self.handler.end('document')


class BasicTextParser(Parser):
    '''
    纯文本解析器
    '''
    def __init__(self, handler):
        super().__init__(handler)
        self.add_rule(ListRule())
        self.add_rule(ListItemRule())
        self.add_rule(TitleRule())
        self.add_rule(HeadingRule())
        self.add_rule(ParagraphRule())

        self.add_filter(r'\*(.+?)\*', 'emphasis')
        self.add_filter(r'(http://[\.a-zA-Z0-9/]+)', 'url')
        self.add_filter(r'([\.a-zA-Z0-9]+@[\.a-zA-Z0-9]+[\.a-zA-Z])', 'mail')


if __name__ == '__main__':
    # 运行程序
    handler = HTMLRenderer()
    parser = BasicTextParser(handler)
    parser.parse(sys.stdin)
