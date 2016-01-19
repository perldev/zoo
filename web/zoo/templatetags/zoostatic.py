# -*- coding: utf-8 -*-

import uuid

from django import template
from django.contrib.staticfiles.templatetags.staticfiles import StaticFilesNode

from core.core import Core

register = template.Library()


class ZooStaticFilesNode(StaticFilesNode):

    core_version = None

    @classmethod
    def get_core_version(cls):
        if not cls.core_version:
            cls.core_version = Core.get_instance().settings.version if Core.is_created() else str(uuid.uuid4())
        return cls.core_version

    def url(self, context):
        return ''.join((super(ZooStaticFilesNode, self).url(context), '?v=', self.get_core_version()))


@register.tag('static')
def do_static(parser, token):
    return ZooStaticFilesNode.handle_token(parser, token)
