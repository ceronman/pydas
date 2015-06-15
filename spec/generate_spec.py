import re
import textwrap
import xml.etree.ElementTree as ElementTree

type_map = {
    'String': 'str'
}


def parse_field_type(field):
    if (field.tag == 'ref'):
        t = field.text.strip()
        return type_map.get(t, t)
    if field.find('ref') is not None:
        return parse_field_type(field.find('ref'))
    elif field.find('list') is not None:
        item = parse_field_type(field.find('list'))
        return '[{}]'.format(item)
    elif field.find('map') is not None:
        key = parse_field_type(field.find('./map/key'))
        value = parse_field_type(field.find('./map/value'))
        return '{{{}: {}}}'.format(key, value)
    elif field.find('union') is not None:
        values = [parse_field_type(v) for v in field.find('union')]
        return '({})'.format(' | '.join(values))
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


def parse_fields(element):
    if element is None:
        return []

    fields = []
    for field_elem in element.findall('field'):
        fields.append({
            'name': field_elem.get('name'),
            'type': parse_field_type(field_elem),
            'doc': parse_element_doc(field_elem)
        })
    return fields


def camelcase_to_underscore(name):
    s1 = re.sub('(.)([A-Z][a-z]+)', r'\1_\2', name)
    return re.sub('([a-z0-9])([A-Z])', r'\1_\2', s1).lower()


def parse_spec(filename):
    root = ElementTree.parse(filename).getroot()

    domains = []
    for domain_elem in root.findall('./body/domain'):
        requests = []
        for request_elem in domain_elem.findall('request'):
            requests.append({
                'name': request_elem.get('method'),
                'params': parse_fields(request_elem.find('params')),
                'result': parse_fields(request_elem.find('result')),
                'doc': parse_element_doc(request_elem),
            })

        notifications = []
        for notification_elem in domain_elem.findall('notification'):
            notifications.append({
                'name': notification_elem.get('event'),
                'params': parse_fields(notification_elem.find('params')),
                'doc': parse_element_doc(notification_elem),
            })
        domains.append({
            'name': domain_elem.get('name'),
            'requests': requests,
            'notifications': notifications,
            'doc': parse_element_doc(domain_elem)
        })

    return {'domains': domains}


def generate_python_api(spec):
    print('from das.server import DartAnalysisServer')
    for domain in spec['domains']:
        print()
        print()
        print("@DartAnalysisServer.register_domain"
              "('{}')".format(domain['name']))
        class_name = domain['name'].capitalize()
        print('class {class_name}Domain:'.format(**locals()))

        indent = '    '
        for i, line in enumerate(domain['doc']):
            if i == 0:
                line = '"""' + line
            else:
                print()

            line = textwrap.fill(line)
            print(textwrap.indent(line, prefix=indent))
        print(textwrap.indent('"""', prefix=indent))

        for request in domain['requests']:

            method = camelcase_to_underscore(request['name'])
            params = [camelcase_to_underscore(p['name'])
                      for p in request['params']]
            params = ', '.join(params + ['*', 'callback=None', 'errback=None'])
            method_def = '    def {method}(self, {params}):'.format(**locals())
            indent = ' ' * (method_def.index('(') + 1)
            line = textwrap.fill(method_def, width=80,
                                 subsequent_indent=indent)
            print()
            print(line)

            indent = '        '
            for i, line in enumerate(request['doc']):
                if i == 0:
                    line = '"""' + line
                else:
                    print()

                line = textwrap.fill(line)
                print(textwrap.indent(line, prefix=indent))

            for param in request['params']:
                if not param['type']:
                    continue
                print()
                name = camelcase_to_underscore(param['name'])
                doc = '\n'.join(param['doc'])
                param_doc = ':param {name}: {doc}'.format(**locals())
                line = textwrap.fill(param_doc, subsequent_indent='    ')
                print(textwrap.indent(line, prefix=indent))
                param_type = ':type {name}: {param[type]}'.format(**locals())
                line = textwrap.fill(param_type, subsequent_indent='    ')
                print(textwrap.indent(line, prefix=indent))

            if request['result']:
                print()
                print(textwrap.indent('Callback arguments:', prefix=indent))

            for param in request['result']:
                if not param['type']:
                    continue
                print()
                name = camelcase_to_underscore(param['name'])
                doc = '\n'.join(param['doc'])
                param_doc = ':param {name}: {doc}'.format(**locals())
                line = textwrap.fill(param_doc, subsequent_indent='    ')
                print(textwrap.indent(line, prefix=indent))
                line = ':type {name}: {param[type]}'.format(**locals())
                print(textwrap.indent(line, prefix=indent))

            print(textwrap.indent('"""', prefix=indent))

            method_name = domain['name'] + '.' + request['name']
            line = "method = '{method_name}'".format(**locals())
            print(textwrap.indent(line, prefix=indent))

            param_values = {p['name']: camelcase_to_underscore(p['name'])
                            for p in request['params']}
            param_values = ', '.join("'{k}': {v}".format(k=k, v=v)
                                     for k, v in param_values.items())
            params_def = 'params = {{{param_values}}}'.format(**locals())
            sub_indent = ' ' * (params_def.index('{') + 1)
            line = textwrap.fill(params_def, width=70,
                                 subsequent_indent=sub_indent)
            print(textwrap.indent(line, prefix=indent))
            kwargs = "callback=callback, errback=errback"
            method = "self.server.request(method, params, {kwargs})"
            print(textwrap.indent(method.format(**locals()), prefix=indent))

        for notification in domain['notifications']:

            method = camelcase_to_underscore(notification['name'])
            method_def = '    def on_{method}(self, *, callback):'
            method_def = method_def.format(**locals())
            print()
            print(method_def)

            indent = '        '
            for i, line in enumerate(notification['doc']):
                if i == 0:
                    line = '"""' + line
                else:
                    print()

                line = textwrap.fill(line)
                print(textwrap.indent(line, prefix=indent))

            if notification['params']:
                print()
                print(textwrap.indent('Callback arguments:', prefix=indent))

            for param in notification['params']:
                if not param['type']:
                    continue
                print()
                name = camelcase_to_underscore(param['name'])
                doc = '\n'.join(param['doc'])
                param_doc = ':param {name}: {doc}'.format(**locals())
                line = textwrap.fill(param_doc, subsequent_indent='    ')
                print(textwrap.indent(line, prefix=indent))
                line = ':type {name}: {param[type]}'.format(**locals())
                print(textwrap.indent(line, prefix=indent))
            print(textwrap.indent('"""', prefix=indent))

            event_name = domain['name'] + '.' + notification['name']
            line = "event = '{event_name}'".format(**locals())
            print(textwrap.indent(line, prefix=indent))
            method = "self.server.notification(event, callback=callback)"
            print(textwrap.indent(method.format(**locals()), prefix=indent))


if __name__ == '__main__':
    spec = parse_spec('spec_input.html')
    generate_python_api(spec)
