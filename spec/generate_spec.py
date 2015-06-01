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

if __name__ == '__main__':
    root = ElementTree.parse('spec_input.html').getroot()

    for domain in root.findall('./body/domain'):
        for request in domain.findall('request'):
            print('REQUEST: ', domain.get('name'), request.get('method'))

            result = None
            result_doc = None
            if request.find('./result/field'):
                result = parse_field_type(request.find('./result/field'))
                result_doc = parse_element_doc(request.find('result'))
            print('\tresult:', repr(result))
            print('\tresult doc:', repr(result_doc))

            params = {}
            param_docs = {}
            for field in request.findall('./params/field'):
                param_name = field.get('name')
                params[param_name] = parse_field_type(field)
                param_docs[param_name] = parse_element_doc(field)

            print('\tparams:', repr(params))
            print('\tparam docs:', repr(param_docs))

            doc_lines = parse_element_doc(request)
            print('\tdoc:', repr(doc_lines))

        for notification in domain.findall('notification'):
            print('EVENT: ', domain.get('name'), notification.get('event'))
            doc_lines = parse_element_doc(notification)
            print('\tdoc:', repr(doc_lines))

            params = {}
            param_docs = {}
            for field in request.findall('./params/field'):
                param_name = field.get('name')
                params[param_name] = parse_field_type(field)
                param_docs[param_name] = parse_element_doc(field)
            print('\tparams:', repr(params))
            print('\tparam docs:', repr(param_docs))
