import requests
import os
import json

def get_post(post_url):
    result = {
        "user_id": "",
        "user_name": "",
        "user_avatar": "",
        "post_id": "",
        "post_content": "",
        "post_time": "",
        "post_images": [],
        "post_videos": [],
        "post_likes": 0,
        "post_comments": 0,
    }
    
    # 从 URL 中提取帖子 ID
    post_id = post_url.split('/')[-1]
    print(f"正在获取帖子 ID: {post_id}")
    
    # 构建 GraphQL 请求
    payload = {
        "operationName": "MessageDetail",
        "variables": {
            "messageId": post_id,
            "messageType": "ORIGINAL_POST"
        },
        "query": open(os.path.join(os.path.dirname(os.path.dirname(__file__)), "query/query_post.graphql")).read()
    }
    
    # 设置请求头和 cookies
    headers = {
        'content-type': 'application/json',
        'origin': 'https://web.okjike.com',
        'sec-ch-ua-platform': '"Windows"',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/108.0.0.0 Safari/537.36'
    }
    
    cookies = {
        'cookie': open(os.path.join(os.path.dirname(os.path.dirname(__file__)), 'config/cookies.txt')).read()
    }
    
    # 发送请求
    response = requests.post("https://web-api.okjike.com/api/graphql", 
                           json=payload,
                           headers=headers,
                           cookies=cookies)
    
    print(f"API 响应状态码: {response.status_code}")
    
    if response.status_code == 200:
        data = response.json()
        print("\nAPI 返回数据结构：")
        print(json.dumps(data, indent=2, ensure_ascii=False))
        
        if 'data' in data and 'message' in data['data']:
            message = data['data']['message']
            print("\n解析到的 message 数据：")
            print(json.dumps(message, indent=2, ensure_ascii=False))
            
            try:
                # 填充结果
                result['user_id'] = message['user']['username']
                result['user_name'] = message['user']['screenName']
                result['user_avatar'] = message['user']['avatarImage']['thumbnailUrl']
                result['post_id'] = message['id']
                result['post_content'] = message['content']
                result['post_time'] = message['createdAt']
                result['post_likes'] = message['likeCount']
                result['post_comments'] = message['commentCount']
                
                # 处理图片
                if 'pictures' in message and message['pictures']:
                    for pic in message['pictures']:
                        result['post_images'].append(pic['picUrl'])
                        
                # 处理视频
                if 'video' in message and message['video']:
                    # 获取视频 URL
                    video_payload = {
                        "operationName": "MediaMetaPlay",
                        "variables": {
                            "messageId": post_id,
                            "messageType": "ORIGINAL_POST"
                        },
                        "query": "query MediaMetaPlay($messageId: ID!, $messageType: MessageType!) {\n  mediaMetaPlay(messageId: $messageId, messageType: $messageType) {\n    mediaLink\n    url\n    __typename\n  }\n}\n"
                    }
                    
                    video_response = requests.post("https://web-api.okjike.com/api/graphql",
                                                 json=video_payload,
                                                 headers=headers,
                                                 cookies=cookies)
                    
                    if video_response.status_code == 200:
                        video_data = video_response.json()
                        if 'data' in video_data and 'mediaMetaPlay' in video_data['data']:
                            result['post_videos'].append(video_data['data']['mediaMetaPlay']['url'])
            except Exception as e:
                print(f"\n处理数据时出错：{str(e)}")
                print("message 数据结构：")
                print(json.dumps(message, indent=2, ensure_ascii=False))
        else:
            print("\n未找到 message 数据")
            if 'errors' in data:
                print("API 返回错误：")
                print(json.dumps(data['errors'], indent=2, ensure_ascii=False))
    
    return result

if __name__ == "__main__":
    # 测试一个包含图片的帖子
    test_url = "https://web.okjike.com/originalPost/67773e6c54198f7f16dc7d6d"
    post_info = get_post(test_url)
    
    # 打印结果
    print("目标帖子：", test_url)
    print("\n获取到的帖子信息：")
    print("用户名称:", post_info['user_name'])
    print("帖子内容:", post_info['post_content'])
    print("发布时间:", post_info['post_time'])
    print("点赞数:", post_info['post_likes'])
    print("评论数:", post_info['post_comments'])
    print("图片数量:", len(post_info['post_images']))
    print("视频数量:", len(post_info['post_videos']))
    
    print("json 如下")
    print(json.dumps(post_info, indent=2, ensure_ascii=False))