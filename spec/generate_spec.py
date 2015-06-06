import re
import textwrap
import xml.etree.ElementTree as ElementTree
from collections import OrderedDict


def parse_field_type(field):
    if (field.tag == 'ref'):
        return field.text.strip()
    if field.find('ref') is not None:
        return parse_field_type(field.find('ref'))
    elif field.find('list') is not None:
        item = parse_field_type(field.find('list'))
        return 'List[{}]'.format(item)
    elif field.find('map') is not None:
        key = parse_field_type(field.find('./map/key'))
        value = parse_field_type(field.find('./map/value'))
        return 'Dict[{}:{}]'.format(key, value)
    elif field.find('union') is not None:
        values = [parse_field_type(v) for v in field.find('union')]
        return 'Union[{}]:'.format(','.join(values))
    else:
        raise Exception("Unknow field type")


def parse_element_doc(element):
    lines = []
    paragraphs = element.findall('p')
    for p in paragraphs:
        parts = []
        for part in p.itertext():
            clean_part = ' '.join(part.split()).strip()
            parts.append(clean_part)
        lines.append(' '.join(parts))
    return lines


def camelcase_to_underscore(name):
    s1 = re.sub('(.)([A-Z][a-z]+)', r'\1_\2', name)
    return re.sub('([a-z0-9])([A-Z])', r'\1_\2', s1).lower()


if __name__ == '__main__':
    root = ElementTree.parse('spec_input.html').getroot()

    for domain in root.findall('./body/domain'):

        print()
        print()
        print("@DartAnalysisServer.register_domain")
        print("class {cls}Domain:".format(cls=domain.get('name').capitalize()))

        for request in domain.findall('request'):
            # print('REQUEST: ', domain.get('name'), request.get('method'))

            result = None
            result_doc = None
            if request.find('./result/field'):
                result = parse_field_type(request.find('./result/field'))
                result_doc = parse_element_doc(request.find('result'))

            params = OrderedDict()
            param_docs = {}
            for field in request.findall('./params/field'):
                param_name = camelcase_to_underscore(field.get('name'))
                params[param_name] = parse_field_type(field)
                param_docs[param_name] = parse_element_doc(field)

            doc_lines = parse_element_doc(request)
            param_names = ', '.join(params)
            method = camelcase_to_underscore(request.get('method'))
            print()
            print('    def {method}({params}):'.format(method=method,
                                                       params=param_names))

            indent = '        '
            print(textwrap.indent(textwrap.fill('"""' + doc_lines[0]),
                                  prefix=indent))
            for line in doc_lines[1:]:
                print()
                print(textwrap.indent(textwrap.fill(line), prefix=indent))
            for param_name in params:
                print()
                param_doc = '\n'.join(param_docs[param_name])
                line = ':param {param}: {doc}'.format(param=param_name,
                                                      doc=param_doc)
                line = textwrap.fill(line, subsequent_indent='    ')
                print(textwrap.indent(line, prefix=indent))
                param_type = params[param_name]
                line = ':type {param}: {type}'.format(param=param_name,
                                                      type=param_type)
                line = textwrap.fill(line, subsequent_indent='    ')
                print(textwrap.indent(line, prefix=indent))

            print(indent + '"""')

        for notification in domain.findall('notification'):
            # print('EVENT: ', domain.get('name'), notification.get('event'))
            doc_lines = parse_element_doc(notification)
            # print('\tdoc:', repr(doc_lines))

            params = {}
            param_docs = {}
            for field in request.findall('./params/field'):
                param_name = field.get('name')
                params[param_name] = parse_field_type(field)
                param_docs[param_name] = parse_element_doc(field)
            # print('\tparams:', repr(params))
            # print('\tparam docs:', repr(param_docs))
