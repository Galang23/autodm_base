import tweepy
import time
import _json
from requests_oauthlib import OAuth1
import requests
import os
from async_upload import VideoTweet

class Twitter:
    def __init__(self):
        print("initializing twitter....")
        self.inits = tweepy.OAuthHandler(os.environ.get("CONSUMER_KEY"), os.environ.get("CONSUMER_SCRET"))
        self.inits.set_access_token(os.environ.get("ACCESS_KEY"), os.environ.get("ACCESS_SECRET"))
        self.api = tweepy.API(self.inits)


    def read_dm(self):
        print("Get direct messages...")
        dms = list()
        try:
            api = self.api
            dm = api.list_direct_messages()
            for x in range(len(dm)):
                sender_id = dm[x].message_create['sender_id']
                message = dm[x].message_create['message_data']['text']
                message_data = str(dm[x].message_create['message_data'])
                json_data = _json.encode_basestring(message_data)
                print(json_data)
                print("Getting message -> "+str(message)+" by sender id "+str(sender_id))

                if "attachment" not in json_data:
                    print("Dm does not have any media...")
                    d = dict(message=message, sender_id=sender_id, id=dm[x].id, media = None, shorted_media_url = None)
                    dms.append(d)
                    dms.reverse()

                else:
                    print("Dm have an attachment..")
                    media_type = dm[x].message_create['message_data']['attachment']['media']['type']
                    print(media_type)
                    if media_type == 'photo':
                        print("It's a photo")
                        attachment = dm[x].message_create['message_data']['attachment']
                        d = dict(message=message, sender_id=sender_id, id=dm[x].id, 
                            media = attachment['media']['media_url'], 
                            shorted_media_url = attachment['media']['url'], type = 'photo')
                        dms.append(d)
                        dms.reverse()
                    elif media_type == 'video':
                        print("It's a video")
                        attachment = dm[x].message_create['message_data']['attachment']
                        media = dm[x].message_create['message_data']['attachment']['media']
                        media_url = media['video_info']['variants'][0]
                        video_url = media_url['url']
                        print("video url : " + str(video_url))
                        d = dict(message=message, sender_id=sender_id, id=dm[x].id, media = video_url,
                            shorted_media_url = attachment['media']['url'], type = 'video')
                        dms.append(d)
                        dms.reverse()
                    elif media_type == 'animated_gif':
                        print("It's a GIF")
                        attachment = dm[x].message_create['message_data']['attachment']
                        media = dm[x].message_create['message_data']['attachment']['media']
                        media_url = media['video_info']['variants'][0]
                        gif_url = media_url['url']
                        print("video url : " + str(video_url))
                        d = dict(message=message, sender_id=sender_id, id=dm[x].id, media = gif_url,
                            shorted_media_url = attachment['media']['url'], type = 'animated_gif')
                        dms.append(d)
                        dms.reverse()

            print(str(len(dms)) + " collected")
            time.sleep(60)
            return dms

        except Exception as ex:
            print(ex)
            time.sleep(60)
            pass


    def delete_dm(self, id):
        print("Deleting dm with id = "+ str(id))
        try:
            self.api.destroy_direct_message(id)
            time.sleep(40)
        except Exception as ex:
            print(ex)
            time.sleep(40)
            pass


    def post_tweet(self, tweet):
        try:
            self.api.update_status(tweet)
        except Exception as e:
            print(e)
            pass

    def post_tweet_with_media(self, tweet, media_url, shorted_media_url, type):
        try:
            print("shorted url" + shorted_media_url)
            print("Downloading media...")
            arr = str(media_url).split('/')
            print(arr[len(arr)-1])
            if type == 'video':
                arr = arr[len(arr)-1].split("?tag=1")
                arr = arr[0]
            elif type == 'photo':
                arr = arr[len(arr)-1]
            if type == 'animated_gif':
                arr = arr[len(arr)-1].split()
                arr = arr[0]

            auth = OAuth1(client_key= os.environ.get("CONSUMER_KEY"),
                          client_secret= os.environ.get("CONSUMER_SCRET"),
                          resource_owner_secret= os.environ.get("ACCESS_SECRET"),
                          resource_owner_key= os.environ.get("ACCESS_KEY")
                         )
            r = requests.get(media_url, auth = auth)
            with open(arr, 'wb') as f:
                f.write(r.content)

            print("Media downloaded successfully!")
            if shorted_media_url in tweet:
                print("shorted url "+ str(shorted_media_url))
                tweet = tweet.replace(shorted_media_url, "")
            else:
                print("kagak ada")
            if type == 'video':
                videoTweet = VideoTweet(arr)
                videoTweet.upload_init()
                videoTweet.upload_append()
                videoTweet.upload_finalize()
                videoTweet.tweet(tweet)
                
                # Jika media variants 0 tidak bisa, maka coba 1. Jika tidak lagi, coba 2
                # Ini hanya temporary fix, perlu dilembutkan
                # Tapi biasanya temporary fix itu malah jadi permanen...
                
                if videoTweet.check_status() == False:
                    # Ini harus dijadikan function supaya rapi
                    print("try 2")
                    print("It's a video")
                    attachment = dm[x].message_create['message_data']['attachment']
                    media = dm[x].message_create['message_data']['attachment']['media']
                    media_url = media['video_info']['variants'][1]
                    video_url = media_url['url']
                    print("video url : " + str(video_url))
                    d = dict(message=message, sender_id=sender_id, id=dm[x].id, media = video_url,
                        shorted_media_url = attachment['media']['url'], type = 'video')
                    dms.append(d)
                    dms.reverse()
                    
                    arr = arr[len(arr)-1].split("?tag=1")
                    arr = arr[0]
                    
                    r = requests.get(media_url, auth = auth)
                    with open(arr, 'wb') as f:
                        f.write(r.content)
                    
                    if shorted_media_url in tweet:
                        print("shorted url "+ str(shorted_media_url))
                        tweet = tweet.replace(shorted_media_url, "")
                    else:
                        print("kagak ada")
                    
                    videoTweet = VideoTweet(arr)
                    videoTweet.upload_init()
                    videoTweet.upload_append()
                    videoTweet.upload_finalize()
                    videoTweet.tweet(tweet)
                    if videoTweet.check_status() == False:
                        print("try 3")
                        print("It's a video")
                        attachment = dm[x].message_create['message_data']['attachment']
                        media = dm[x].message_create['message_data']['attachment']['media']
                        media_url = media['video_info']['variants'][2]
                        video_url = media_url['url']
                        print("video url : " + str(video_url))
                        d = dict(message=message, sender_id=sender_id, id=dm[x].id, media = video_url,
                            shorted_media_url = attachment['media']['url'], type = 'video')
                        dms.append(d)
                        dms.reverse()
                        
                        arr = arr[len(arr)-1].split("?tag=1")
                        arr = arr[0]
                    
                        r = requests.get(media_url, auth = auth)
                        with open(arr, 'wb') as f:
                            f.write(r.content)
                    
                        if shorted_media_url in tweet:
                            print("shorted url "+ str(shorted_media_url))
                            tweet = tweet.replace(shorted_media_url, "")
                        else:
                            print("kagak ada")
                        
                        videoTweet = VideoTweet(arr)
                        videoTweet.upload_init()
                        videoTweet.upload_append()
                        videoTweet.upload_finalize()
                        videoTweet.tweet(tweet)
            elif type == 'photo':
                self.api.update_with_media(filename=arr, status=tweet)
            elif type =='animated_gif':
                videoTweet = VideoTweet(arr)
                videoTweet.upload_init()
                videoTweet.upload_append()
                videoTweet.upload_finalize()
                videoTweet.tweet(tweet)
                
            os.remove(arr)
            
            print("Upload with media success!")
            
        except Exception as e:
            print(e)
            pass
