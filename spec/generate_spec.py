import textwrap
import xml.etree.ElementTree as ElementTree


class Method:
    def __init__(self, domain, name, args, result):
        self.domain = domain
        self.name = name
        self.args = args,
        self.result = result

if __name__ == '__main__':
    root = ElementTree.parse('spec_input.html').getroot()

    for domain in root.findall('./body/domain'):
        for request in domain.findall('request'):
            print(domain.get('name'), request.get('method'))

            if request.findall('result'):
                print('\t has result')

            params = request.findall('params')
            if params:
                print('\t has params')

            paragraphs = request.findall('p')
            for p in paragraphs:
                parts = []
                for part in p.itertext():
                    clean_part = ' '.join(part.split()).strip()
                    parts.append(clean_part)
                parts = ' '.join(parts)
                print(textwrap.fill(parts, initial_indent='    '))