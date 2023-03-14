from kubernetes import client, config
import json

def main():
    config.load_kube_config()
    print_node_information()
    print_pod_information()


def print_pod_information():
    cust = client.CustomObjectsApi()
    pod_metric=cust.list_cluster_custom_object('metrics.k8s.io', 'v1beta1', 'pods')
    pod_status_dict = {}
    total_status_list = []
    for pod in pod_metric['items']:
        data = pod['containers'][0]['usage']
        pod_status_dict['pod_cpu'] = data['cpu']
        pod_status_dict['pod_memory'] = data['memory']
        pod_status_dict['pod_name'] = pod['metadata']['name']
        pod_status_dict['namespace'] = pod['metadata']['namespace']
        total_status_list.append(pod_status_dict.copy())

    writeFile(total_status_list)


def search_node_status(node):
    for item in node.status.conditions:
        if item.type.lower() == 'ready':
            if item.status.lower() == 'true':
                return 'Ready'
            else:
                return 'Not Ready'

def print_node_information():
    v1 = client.CoreV1Api()
    cust = client.CustomObjectsApi()
    nodes = v1.list_node().items
    node_status_dict = {}
    total_status_list = []
    node_metric_dict = {}
    total_metric_list = []
    result = []
    for node in nodes:
        node_status_dict['node_name'] = node.metadata.name
        node_status_dict['status'] = search_node_status(node)
        total_status_list.append(node_status_dict.copy())
    
    nodes_metric = cust.list_cluster_custom_object('metrics.k8s.io', 'v1beta1', 'nodes')  
    for node in nodes_metric['items']:
        data = node['usage']
        node_metric_dict['node_cpu'] = data['cpu']
        node_metric_dict['memory'] = data['memory']
        node_metric_dict['node_name'] = node['metadata']['name']
        total_metric_list.append(node_metric_dict.copy())
    
    for i in range(len(total_status_list)):
        merged_dict = total_status_list[i].copy()
        merged_dict.update(total_metric_list[i])
        result.append(merged_dict)

    writeFile(result)

def writeFile(input):
    file1 = open('k8s_metric.log', 'a')
    for i in input:
        file1.write(json.dumps(i)+'\n') 
    file1.close()

main()