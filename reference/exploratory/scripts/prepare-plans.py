"""Generate timed comparison plans from the course plans, preserving the course examples."""
from pathlib import Path
import xml.etree.ElementTree as ET

base = Path(__file__).resolve().parents[2] / '5. SpringAOP/jmeter'
for operation in ['ReadProduct', 'WriteProduct']:
    tree = ET.parse(base / (operation + '.jmx'))
    root = tree.getroot()
    group = root.find('.//ThreadGroup')
    ET.SubElement(group, 'stringProp', name='ThreadGroup.scheduler').text = '${__P(timed,false)}'
    ET.SubElement(group, 'stringProp', name='ThreadGroup.duration').text = '${__P(duration,35)}'
    sampler = root.find('.//HTTPSamplerProxy')
    sampler.set('testname', operation)
    for prop, value in [('HTTPSampler.connect_timeout', '5000'),
                        ('HTTPSampler.response_timeout', '15000')]:
        ET.SubElement(sampler, 'stringProp', name=prop).text = value
    for parent in root.iter():
        children = list(parent)
        if sampler in children:
            assertions = children[children.index(sampler) + 1]
            break
    if operation == 'WriteProduct':
        body = sampler.find('.//stringProp[@name="Argument.value"]')
        body.text = ('{"name":"LAB3-${__P(run.id,smoke)}-${__threadNum}-${__counter(TRUE,)}",'
                     '"originalPrice":100,"weight":100,"barcode":"lab3-comparison",'
                     '"unit":"box","originPlace":"Xiamen"}')
        assertion = ET.SubElement(assertions, 'JSONPathAssertion', guiclass='JSONPathAssertionGui',
            testclass='JSONPathAssertion', testname='Business success', enabled='true')
        for key, val in [('JSON_PATH', '$.errno'), ('EXPECTED_VALUE', '1')]:
            ET.SubElement(assertion, 'stringProp', name=key).text = val
        for key, val in [('JSONVALIDATION','true'),('EXPECT_NULL','false'),('INVERT','false'),('ISREGEX','false')]:
            ET.SubElement(assertion, 'boolProp', name=key).text = val
        ET.SubElement(assertions, 'hashTree')
    extract = ET.SubElement(assertions, 'JSONPostProcessor', guiclass='JSONPostProcessorGui',
                           testclass='JSONPostProcessor', testname='Record product ID', enabled='true')
    for key,val in [('JSONPostProcessor.referenceNames','response_id'),
                    ('JSONPostProcessor.jsonPathExprs','$.data.id'),
                    ('JSONPostProcessor.match_numbers','1'),
                    ('JSONPostProcessor.defaultValues','MISSING')]:
        ET.SubElement(extract,'stringProp',name=key).text=val
    ET.SubElement(assertions,'hashTree')
    assertion = ET.SubElement(assertions, 'JSONPathAssertion', guiclass='JSONPathAssertionGui',
        testclass='JSONPathAssertion', testname='Returned product ID', enabled='true')
    for key,val in [('JSON_PATH','$.data.id'),('EXPECTED_VALUE','${id}' if operation=='ReadProduct' else '[1-9][0-9]*')]:
        ET.SubElement(assertion,'stringProp',name=key).text=val
    for key,val in [('JSONVALIDATION','true'),('EXPECT_NULL','false'),('INVERT','false'),('ISREGEX','true')]:
        ET.SubElement(assertion,'boolProp',name=key).text=val
    ET.SubElement(assertions,'hashTree')
    ET.indent(tree)
    tree.write(base / (operation + 'Comparison.jmx'),encoding='utf8',xml_declaration=True)
    print('Generated', operation + 'Comparison.jmx')
