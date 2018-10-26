import json, requests, time, ast, click


aws_region = "sa-east-1"

def get_api_json(event_url):
  return json.loads(requests.get(event_url).text)

api_url = "https://pricing.us-east-1.amazonaws.com/offers/v1.0/aws/AmazonEC2/current/"+aws_region+"/index.json"

offer = get_api_json(api_url)

formatado = {}

for sku, attrs in offer['products'].items():
 a = attrs['attributes']

 if not ('location' in a and 
    'locationType' in a and
    'instanceType' in a):
   continue

 formatado[sku] = [a['locationType'], \
                  a['location'], \
                  a['instanceType'], \
                  a['vcpu'], \
                  a['memory'].split(" GiB")[0], \
                  a['operatingSystem'], \
                  a['tenancy']]

for ond in offer['terms']['OnDemand']:
 o = offer['terms']['OnDemand'][ond]
 for i in o:
   for key in o[i]['priceDimensions']:
    pricePerUnit = ast.literal_eval(o[i]['priceDimensions'][key]['pricePerUnit']['USD'])
    if not (ond in formatado): continue
    formatado[ond].append(pricePerUnit)

# List index
# 0    "AWS Region",
# 1    "South America (Sao Paulo)",
# 2    "r4.xlarge",
# 3   "4",
# 4   "30.5",
# 5    "Linux",
# 6   "Shared",
# 7    0.56
def get_cheaper_vcpu(d,vcpu_qty,term='OnDemand',tenancy='Shared',os='Linux'):
 index = 0
 for i in d:
  if (index == 0): 
   choice= d[i][2]
   choice_price = d[i][-1]
   if(choice_price == 0.0): continue
   index = index+1
   
  vcpus = d[i][3]
  price = d[i][-1]
  ec2_instance = d[i][2]
  os_instance  = d[i][5]
  if (os_instance != os or
    d[i][6] != 'Shared'): continue

  if(price == 0.0000): continue

  if (int(vcpus) >= int(vcpu_qty)):
   if (price < choice_price):
    choice = ec2_instance
    choice_price = price
 return (choice,choice_price)

#jf = json.dumps(formatado)
#print(jf)

melhor_4vcpu = get_cheaper_vcpu(formatado,32)
print(json.dumps(melhor_4vcpu))
