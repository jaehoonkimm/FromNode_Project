from django.shortcuts import render, redirect
from .models import Nodes
from FileApp.models import Files
from ProjectApp.models import Projects
from django.contrib.auth.models import User
from datetime import datetime
from django.core import serializers
from UserApp.models import Profile

def get_location_list(dbData):
    #str타입 리스트 만들기
    li_numMentioned =[]
    num_mentioned = 0
    node_count = 1
    for obj in dbData:
        if obj.previousCode == None:
            li_numMentioned.append([obj.Code, num_mentioned, obj.previousCode, node_count, obj.createdDate])
            node_count += 1
        else:
            li_numMentioned.append([obj.Code, num_mentioned, obj.previousCode.Code, node_count, obj.createdDate])
            node_count += 1
    
    li_numMentioned.sort(key=lambda x: x[4])
    print("여기부터 봐라")
    print(li_numMentioned)
    #노드별 브랜치 파생 여부 구하기(언급횟수 구하기)
    for i in range(0,len(li_numMentioned)):
        search_target = li_numMentioned[i][0] #자 내 코드는 이것이다
        searched_men_num = 0
        for j in range(i,len(li_numMentioned)): #다른애들의 previous와 내 코드를 비교해보아라
            if li_numMentioned[j][2] == search_target:
                searched_men_num += 1
                li_numMentioned[i][1] = searched_men_num
    
    #배치시작
    li_last = []
    li_temp = []
    li_location = [] #최종으로 넘겨줄 노드 좌표리스트. [x넘버(열번호),브랜치넘버(행번호),노드코드] 로 저장됨
    is_started = False
    for n, node in enumerate(li_numMentioned):
        print("지금 배치할것이 머냐면 " + node[0])
        print("누구 뒤냐면 " + str(node[2]))
        if is_started == False: #첫 노드
            print("첫 노드 찾았다")
            li_temp.append([node[0]])
            li_last.append(node[0])
            is_started = True
        else:
            if node[2] in li_last: #따라갈 놈이 끝놈이면
                print("따라갈 놈이 있네")
                for i, sublist in enumerate(li_temp):
                    if node[2] in sublist: #내 앞에놈이 있는 행에 추가하자
                        li_temp[i].append(node[0])
                        break
                for k, endnode in enumerate(li_last):
                    if endnode == node[2]:
                        print("끝놈정보에 내껄로 업뎃할게" + node[0])
                        li_last[k] = node[0]
                        break
            else: #새 브랜치 생성해야 되면 순서 파악 후에 그 위치에 생성
                for i, sublist in enumerate(li_temp):
                    if node[2] in sublist:
                        li_temp.insert(i+1, [node[0]])
                        li_last.insert(i+1,node[0])
                        break

    num_of_branch = len(li_temp)
    
    for y, sublist in enumerate(li_temp):
        for node in sublist:
            code = node
            for i in range(0,len(li_numMentioned)):
                if li_numMentioned[i][0] == code:
                    xLoc = li_numMentioned[i][3]
                    li_location.append([xLoc, y+1, str(code)])
                    break
    
    print(li_location)
    # print(li_last)

    return li_location, num_of_branch, node_count

def node_list(request,file_Code):
    if request.user.is_authenticated:
        proj_obj = Projects.objects.filter(members = request.user)
    else:
        pass
    The_File = Files.objects.get(Code=file_Code)
    print("The file")
    print(The_File)
    project = The_File.ownerPCode
    pro_name = project.name
    node_objs = Nodes.objects.filter(ownerFCode = The_File)
    proj_user = project.members.all()
 

    json_data = serializers.serialize("json", Nodes.objects.filter(ownerFCode = The_File.Code))
    print(json_data)
    user_data = serializers.serialize("json", User.objects.all())
    if True:
        dbData = Nodes.objects.filter(ownerFCode = The_File.Code)
        tuple_return = get_location_list(dbData)
        li_location = tuple_return[0]
        num_of_row = tuple_return[1]
        num_of_column = tuple_return[2] 

    gridRowWidth = "100px "
    gridColumnHeight = "100px "
    gridRowNum = gridRowWidth * num_of_row
    gridColumnNum = gridColumnHeight * num_of_column

    objects = {
        "li_location":li_location,
        "gridRowNum":gridRowNum,
        "gridColumnNum":gridColumnNum,
        "num_of_row":num_of_row, 
        "num_of_column":num_of_column, 
        "proj_obj":proj_obj,
        "node_objs":node_objs,
        "The_File":The_File, 
        "json":json_data,
        "proj_user":proj_user,
        "user_data" : user_data,
        "pro_name" : pro_name
    }  
    return render(request, 'NodeApp/node_list.html', objects)

def node_detail(request,node_Code):
    node_obj = Nodes.objects.filter(Code = node_Code)
    The_file = Nodes.objects.get(Code=node_Code).ownerFCode

    return render(request, 'NodeApp/node_details.html', {'node_obj':node_obj,'The_file':The_file})

def create_node(request):
    # 나중에 쓰일 수도 ? 클릭한 노드 정보 일단 담아뒀음
    NodeComment = request.POST['NodeComment']
    NodeCreatedDate = request.POST['NodeCreatedDate']
    NodeDescription = request.POST['NodeDescription']
    NodeFileObj = request.POST['NodeFileObj']
    NodeName = request.POST['NodeName']
    NodeOwnerFileCode = request.POST['NodeOwnerFileCode']
    NodeOwnerProjectCode = request.POST['NodeOwnerProjectCode']
    NodePreviousCode = request.POST['NodePreviousCode']
    NodeOwner = request.POST['NodeOwner']
    NodePk = request.POST['NodePk']
    redirectURL = '/node/node_list/'+str(NodeOwnerFileCode)
    
    clickedNode = Nodes.objects.get(Code=int(NodePk))
    print(request.user)
    # 파일없을 때 예외 처리 해야합니다
    if request.method == 'POST':
        node_object = Nodes()
        node_object.fileObj = request.FILES['uploadFile']
        node_object.previousCode = clickedNode
        node_object.ownerFCode = clickedNode.ownerFCode
        node_object.ownerPCode = clickedNode.ownerPCode
        node_object.whoIsOwner = request.user
        node_object.save()
        return redirect(redirectURL)
    return redirect(redirectURL)


