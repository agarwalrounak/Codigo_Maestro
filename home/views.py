from django.shortcuts import render
from django.shortcuts import HttpResponse, HttpResponseRedirect, reverse
import requests, json, time
from operator import itemgetter

access_token = None
api_call_headers = None
username = None
institution =None
usernameR=None


# Create your views here.
# index view
def index(request):
    context = {
        'authorize_url': "https://api.codechef.com/oauth/authorize",
        'token_url': "https://api.codechef.com/oauth/token",
        'callback_uri': "http://127.0.0.1:8000/home/auth/",
        'client_id': <client_id>,
        'client_secret': <client_Secret>,
    }
    if access_token:
        return render(request, "home/details.html", {'example': 'example'})
    else:
        return render(request, "home/index.html", context)

# Authentication purpose
def auth(request):
    global access_token, api_call_headers
    if access_token != None:
        return HttpResponseRedirect(reverse('home:index'))
    authorization_code = request.GET['code']
    headers = {
        'content-type': 'application/json',
    }
    Data = {'grant_type': 'authorization_code', 'code': authorization_code,
            'client_id': "b529d558182948e92f80fa9d2b42b99d",
            'client_secret': "fac9653c2e7dd282bbdd3218fd92e085", 'redirect_uri': "http://127.0.0.1:8000/home/auth/"}
    access_token_response = requests.post("https://api.codechef.com/oauth/token", data=json.dumps(Data),
                                          headers=headers)
    tokens = json.loads(access_token_response.text)
    access_token = tokens["result"]["data"]["access_token"]
    api_call_headers = {'Authorization': 'Bearer ' + access_token}
    return HttpResponseRedirect(reverse('home:details'))


#logout
def logout(request):
    global access_token
    access_token = None
    time.sleep(2)
    return HttpResponseRedirect(reverse('home:index'))

# details page

def details(request):
    global access_token, username, institution,usernameR
    test_url = "https://api.codechef.com/users/me"
    parameters = {
        'fields': 'fullname, country',
    }
    api_call_response = requests.get(test_url, headers=api_call_headers, params=parameters)
    detail_user = json.loads(api_call_response.text)
    username = detail_user["result"]["data"]["content"]["username"]
    rating = detail_user["result"]["data"]["content"]["band"]
    usernameR = rating + ' '+ username
    fullname = detail_user["result"]["data"]["content"]["fullname"]
    institution = detail_user["result"]["data"]["content"]["organization"]

    if access_token:
        return render(request, "home/details.html", {'usernameR': usernameR, 'fullname': fullname, 'detail_user': detail_user, 'username': username})
    else:
        return HttpResponseRedirect(reverse('home:index'))



# for ranking of institution
def rankings(request):
    userrank = None
    contestCode = request.POST["contest"]
    institute= request.POST["institute"]

    question_url = "https://api.codechef.com/contests/" + contestCode
    para = {
        'fields': 'problemsList',
        'sortBy': 'problemCode',
        'sortOrder': 'asc'
    }
    api_call_response = requests.get(question_url, headers=api_call_headers, params=para)
    Questions = json.loads(api_call_response.text)

    if "data" in Questions["result"]:
        queslist = Questions["result"]["data"]["content"]["problemsList"]
    else:
        return render(request, "home/error.html", {'error': 'Fields are wrong. Please check the fields again! '})

    codelist = []
    for i in queslist:
        codelist = codelist + [i['problemCode']]

    ranklist=[]
    userranklist = []
    val = 0
    rankings = None
    length = 1500
    # For general rank list
    while length == 1500:
        dummy = None
        rank_url = "https://api.codechef.com/rankings/" + contestCode
        parameters = {
            'fields': 'username, rank, problemScore, totalScore',
            'institution': institute,
            'offset': val,
            'limit': '1500',
            'sortBy': 'rank',
            'sortOrder': 'asc',
        }

        api_call_response = requests.get(rank_url, headers=api_call_headers, params=parameters)
        rankings = json.loads(api_call_response.text)
        if "content" in rankings["result"]["data"]:
            dummy=rankings["result"]["data"]["content"]
        else:
            return render(request, "home/error.html", {'error': 'cant apply filter to the desired institution'})

        length = len(dummy)
        ranklist = ranklist + dummy
        val = val + 1500


    # For user rank details
    val = 0
    length = 1500
    while length == 1500:
        dummy = None
        rank_url = "https://api.codechef.com/rankings/" + contestCode
        parameters = {
            'fields': 'username, rank, problemScore, totalScore',
            'institution': institution,
            'offset': val,
            'limit': '1500',
            'sortBy': 'rank',
            'sortOrder': 'asc',
        }

        api_call_response = requests.get(rank_url, headers=api_call_headers, params=parameters)
        userrankings = json.loads(api_call_response.text)
        if "content" in userrankings["result"]["data"]:
            dummy = userrankings["result"]["data"]["content"]
        else:
            break
        length = len(dummy)
        userranklist = userranklist + dummy
        val = val + 1500

    for i in userranklist:
        if i['username'] == username:
            userrank = i
            break
    if userrank and institute != institution:
        ranklist = ranklist + [userrank]

    for i in ranklist:
        i['rank'] = int(i['rank'])

    ranklist.sort(key=itemgetter('rank'))


    ranks = []
    users = []
    score = []
    scores = []
    for i in ranklist:
        ranks = ranks + [i['rank']]
        users = users + [i['username']]
        score = score + [i['totalScore']]
        s = []
        for code in codelist:
            flag = 0
            li = i['problemScore']
            for j in li:
                if code == j['problemCode']:
                    s = s + [j['score']]
                    flag = 1

            if not flag:
                s = s + [0]
        scores.append(s)

    data = zip(users, ranks, score, scores)
    data = list(data)
    if access_token:
        return render(request, "home/rankings.html", {'data': data,'username': username, 'institute': institute, 'usernameR': usernameR, 'userrank':userrank, 'codelist': codelist})
    else:
        return HttpResponseRedirect(reverse('home:index'))





#Problems Rating according practice questions

a = []
b = []
c = []
d = []
e = []
f = []
g = []
def problems(request):
    global a,b,c,d,e,f,g
    color = None
    type = request.POST["Value"]
    data_list = []
    if type == "1 Star":
        data_list = a
        color ='#F4F6F6'
    elif type == "2 Star":
        data_list = b
        color = '#EAFAF1'
    elif type == "3 Star":
        data_list = c
        color = '#EAF2F8'
    elif type == "4 Star":
        data_list = d
        color = '#EBDEF0'
    elif type == "5 Star":
        data_list = e
        color = '#FCF3CF'
    elif type == "6 Star":
        data_list = f
        color = '#FDEBD0'
    elif type == "7 Star":
        data_list = g
        color = '#FADBD8'

    data_list.sort(key=itemgetter('successfulSubmissions'), reverse=True)
    if access_token:
        return render(request, "home/problems.html", {'data': data_list, 'type': type, 'color': color, 'code': 'problemCode', 'username':username, 'usernameR':usernameR})
    else:
        return HttpResponseRedirect(reverse('home:index'))



def rating(request):

    global a,b,c,d,e,f,g
    a = []
    b = []
    c = []
    d = []
    e = []
    f = []
    g = []

    question =[]
    questions = "https://api.codechef.com/problems/school"
    parameters = {
        'fields': 'problemCode, problemName, successfulSubmissions, accuracy',
        'offset': 0,
        'limit': 100,
        'sortOrder': 'desc'
    }
    dummy = None

    api_call_response = requests.get(questions, headers=api_call_headers, params=parameters)
    question_list = json.loads(api_call_response.text)

    #if "content" in question_list["result"]["data"]:
    dummy = question_list["result"]["data"]["content"]

    question = question + dummy
    # return HttpResponse(question)

    questions = "https://api.codechef.com/problems/easy"
    parameters = {
        'fields': 'problemCode, problemName, successfulSubmissions, accuracy',
        'offset': 0,
        'limit': 100,
        'sortOrder': 'desc'
    }
    dummy = None

    api_call_response = requests.get(questions, headers=api_call_headers, params=parameters)
    question_list = json.loads(api_call_response.text)

    #if "content" in question_list["result"]["data"]:
    dummy = question_list["result"]["data"]["content"]

    question = question + dummy

    questions = "https://api.codechef.com/problems/medium"
    parameters = {
        'fields': 'problemCode, problemName, successfulSubmissions, accuracy',
        'offset': 0,
        'limit': 100,
        'sortOrder': 'desc'
    }
    dummy = None

    api_call_response = requests.get(questions, headers=api_call_headers, params=parameters)
    question_list = json.loads(api_call_response.text)

    #if "content" in question_list["result"]["data"]:
    dummy = question_list["result"]["data"]["content"]

    question = question + dummy

    questions = "https://api.codechef.com/problems/hard"
    parameters = {
        'fields': 'problemCode, problemName, successfulSubmissions, accuracy',
        'offset': 0,
        'limit': 100,
        'sortOrder': 'desc'
    }
    dummy = None

    api_call_response = requests.get(questions, headers=api_call_headers, params=parameters)
    question_list = json.loads(api_call_response.text)

    #if "content" in question_list["result"]["data"]:
    dummy = question_list["result"]["data"]["content"]

    question = question + dummy
    # return HttpResponse(question)

    questions = "https://api.codechef.com/problems/extcontest"
    parameters = {
        'fields': 'problemCode, problemName, successfulSubmissions, accuracy',
        'offset': 0,
        'limit': 100,
        'sortOrder': 'desc'
    }
    dummy = None

    api_call_response = requests.get(questions, headers=api_call_headers, params=parameters)
    question_list = json.loads(api_call_response.text)

    # if "content" in question_list["result"]["data"]:
    dummy = question_list["result"]["data"]["content"]

    question = question + dummy


    for i in question:
        if i['successfulSubmissions'] >= 10500:
            a = a + [i]

        if i['successfulSubmissions'] >= 10000 and i['successfulSubmissions'] <= 40000:
            b = b + [i]

        if i['successfulSubmissions'] >= 5000 and i['successfulSubmissions'] <= 20000:
            c = c + [i]

        if i['successfulSubmissions'] >= 1000 and i['successfulSubmissions'] <= 5050:
            d = d + [i]

        if i['successfulSubmissions'] >= 300 and i['successfulSubmissions'] <= 1150:
            e = e + [i]

        if i['successfulSubmissions'] >= 100 and i['successfulSubmissions'] <= 330:
            f = f + [i]

        if i['successfulSubmissions'] >= 0 and i['successfulSubmissions'] <= 120:
            g = g + [i]

    if access_token:
        return render(request, "home/contest_questions.html", {'context': 'example', 'usernameR': usernameR, 'username': username})
    else:
        return HttpResponseRedirect(reverse('home:index'))



#Profile Comparator

def comparator(request):
    user1 = request.POST["user1"]
    user2 = request.POST["user2"]
    users_url = 'https://api.codechef.com/users/'
    user1_url = users_url + user1
    user2_url = users_url + user2
    rankings_url = 'https://api.codechef.com/rankings/'
    '''
    fields = {
            'fields': 'username, fullname, country, state, city, rankings, ratings, occupation, organization, language',
        }
    '''

    practice_problems1=None
    practice_problems2=None
    user1_response = requests.get(user1_url, headers=api_call_headers)
    data_received = json.loads(user1_response.text)
    if 'content' in data_received['result']['data']:
        content1 = data_received['result']['data']['content']
    else:
        return render(request, 'home/error.html', {'error': 'Fields are wrong. Please check the fields again! '})

    user2_response = requests.get(user2_url, headers=api_call_headers)
    data_received = json.loads(user2_response.text)
    if 'content' in data_received['result']['data']:
        content2 = data_received['result']['data']['content']
    else:
        return render(request, 'home/error.html', {'error': 'Fields are wrong. Please check the fields again! '})

    contests1_list = []
    problems1 = content1['problemStats']['partiallySolved']
    for key, value in problems1.items():
        contests1_list.append(key)
    problems1 = content1['problemStats']['solved']
    for key, value in problems1.items():
        if key not in contests1_list:
            contests1_list.append(key)

    contests2_list = []
    problems2 = content2['problemStats']['partiallySolved']
    for key, value in problems2.items():
        contests2_list.append(key)
    problems2 = content2['problemStats']['solved']
    for key, value in problems2.items():
        if key not in contests2_list:
            contests2_list.append(key)

    contests1_list = set(contests1_list)
    contests2_list = set(contests2_list)
    if contests1_list & contests2_list:
        contests_list = contests1_list & contests2_list
        common_contests = [contest for contest in contests_list if "Practice" not in contest]
    else:
        common_contests = []

    common_contests_ranking1 = []
    common_contests_ranking2 = []

    for contest in common_contests:
        contest_rankings_url = rankings_url + contest

        parameters = {
            'fields': 'rank, username',
            'institution': content1['organization'],
            'offset': 0,
            'limit': 1500,
            'sortBy': 'rank',
            'sortOrder': 'asc',
        }
        rankings_response = requests.get(contest_rankings_url, headers=api_call_headers, params=parameters)
        rankings_list = json.loads(rankings_response.text)
        rank_list = rankings_list['result']['data']['content']
        for content in rank_list:
            if content['username'] == content1['username']:
                common_contests_ranking1.append(content['rank'])
                break

        parameters = {
            'fields': 'rank, username',
            'institution': content2['organization'],
            'offset': 0,
            'limit': 1500,
            'sortBy': 'rank',
            'sortOrder': 'asc',
        }
        rankings_response = requests.get(contest_rankings_url, headers=api_call_headers, params=parameters)
        rankings_list = json.loads(rankings_response.text)
        rank_list = rankings_list['result']['data']['content']
        for content in rank_list:
            if content['username'] == content2['username']:
                common_contests_ranking2.append(content['rank'])
                break

    common_ranks = zip(common_contests, common_contests_ranking1, common_contests_ranking2)

    cook_off1 = 0
    cook_off2 = 0
    long_challenge1 = 0
    long_challenge2 = 0
    lunchtime1 = 0
    lunchtime2 = 0
    months = ["JAN", "FEB", "MARCH", "APRIL", "MAY", "JUNE", "JULY", "AUG", "SEPT", "OCT", "NOV", "DEC"]

    solved1 = content1['problemStats']['solved']
    for contestCode, problems in solved1.items():
        if contestCode.startswith('Practice'):
            practice_problems1 = len(problems)
        elif contestCode.startswith(tuple(months)):
            long_challenge1 = long_challenge1 + len(problems)
        elif contestCode.startswith('COOK'):
            cook_off1 = cook_off1 + len(problems)
        elif contestCode.startswith('LTIME'):
            lunchtime1 = lunchtime1 + len(problems)

    solved2 = content2['problemStats']['solved']
    for contestCode, problems in solved2.items():
        if contestCode.startswith('Practice'):
            practice_problems2 = len(problems)
        elif contestCode.startswith(tuple(months)):
            long_challenge2 = long_challenge2 + len(problems)
        elif contestCode.startswith('COOK'):
            cook_off2 = cook_off2 + len(problems)
        elif contestCode.startswith('LTIME'):
            lunchtime2 = lunchtime2 + len(problems)



    context = {
        'username1': content1['username'],
        'fullname1': content1['fullname'],
        'occupation1': content1['occupation'],
        'organization1': content1['organization'],
        'city1': content1['city']['name'],
        'state1': content1['state']['name'],
        'country1': content1['country']['name'],
        'current_rating1': content1['ratings']['allContest'],
        'practice_problems1': practice_problems1,
        'long_challenge1': long_challenge1,
        'cook_off1': cook_off1,
        'lunchtime1': lunchtime1,

        'username2': content2['username'],
        'fullname2': content2['fullname'],
        'occupation2': content2['occupation'],
        'organization2': content2['organization'],
        'city2': content2['city']['name'],
        'state2': content2['state']['name'],
        'country2': content2['country']['name'],
        'current_rating2': content2['ratings']['allContest'],
        'practice_problems2': practice_problems2,
        'long_challenge2': long_challenge2,
        'cook_off2': cook_off2,
        'lunchtime2': lunchtime2,
        'username':username,
        'usernameR': usernameR,
        'common_ranks': common_ranks,

    }

    return render(request, 'home/comparator.html', context)




def error_404_view(request, exception):
    data = {"error": "page not found"}
    return render(request,'home/error_404.html', data)