import re
import textwrap
import xml.etree.ElementTree as ElementTree


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
            "name": domain_elem.get('name'),
            "requests": requests,
            "notifications": notifications
        })

    return {'domains': domains}


def generate_python_api(spec):
    for domain in spec['domains']:
        print()
        print()
        class_name = domain.get('name').capitalize()
        print('class {class_name}Domain:'.format(**locals()))

        for request in domain['requests']:

            method = camelcase_to_underscore(request['name'])
            params = [camelcase_to_underscore(p['name'])
                      for p in request['params']]
            params = ', '.join(params + ['*', 'callback=None', 'errback=None'])
            method_def = '    def {method}({params})'.format(**locals())
            indent = ' ' * (method_def.index('(') + 1)
            line = textwrap.fill(method_def, width=80,
                                 subsequent_indent=indent)
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
                line = ':type {name}: {param[type]}'.format(**locals())
                print(textwrap.indent(line, prefix=indent))
            print(textwrap.indent('"""', prefix=indent))


if __name__ == '__main__':
    spec = parse_spec('spec_input.html')
    generate_python_api(spec)
