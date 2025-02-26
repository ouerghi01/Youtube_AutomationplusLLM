from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support.ui import WebDriverWait
from moviepy.editor import VideoFileClip, AudioFileClip, concatenate_audioclips
from gtts import gTTS
import json 
from selenium.webdriver.support import expected_conditions as EC
import time
import torch
from agent import Agent

import undetected_chromedriver as uc
import os
import numpy as np 
import cv2
from dotenv import load_dotenv

from selenium.common.exceptions import NoSuchElementException, TimeoutException, StaleElementReferenceException
torch.cuda.empty_cache()

load_dotenv()  

def authenticate_user(email, password, base_url):
    options = uc.ChromeOptions()
    options.user_data_dir = "c:\\temp\\profile"
    driver = uc.Chrome(
    options = options 
    )  
    driver.delete_all_cookies()
    driver.get(base_url)
    time.sleep(5)

    try:
        connexion= WebDriverWait(
        driver, 20).until(EC.presence_of_element_located((By.XPATH, '/html/body/ytd-app/div[1]/div[2]/ytd-masthead/div[4]/div[3]/div[2]/ytd-button-renderer/yt-button-shape/a/yt-touch-feedback-shape/div/div[2]')))
        connexion.click()
        
        try:
            identifiant= WebDriverWait(
            driver, 10).until(EC.presence_of_element_located((By.ID, 'identifierId')))
            identifiant.send_keys(email)
            suivant= WebDriverWait(
            driver, 10).until(EC.presence_of_element_located((By.XPATH, '/html/body/div[1]/div[1]/div[2]/c-wiz/div/div[3]/div/div[1]/div/div/button')))
            ActionChains(driver).move_to_element(suivant).click(suivant).perform()
        except (NoSuchElementException, TimeoutException, StaleElementReferenceException) as e:
            email_exist=driver.find_element(By.XPATH, '/html/body/div[1]/div[1]/div[2]/div/div/div[2]/div/div/div/form/span/section/div/div/div/div/ul/li[1]/div/div[1]/div/div[2]/div[1]')
            if email_exist:
                print("Email already exists")
                ActionChains(driver).move_to_element(email_exist).click(email_exist).perform()
        time.sleep(10)
        password= driver.find_element(By.XPATH, '/html/body/div[1]/div[1]/div[2]/c-wiz/div/div[2]/div/div/div/form/span/section[2]/div/div/div[1]/div[1]/div/div/div/div/div[1]/div/div[1]/input').send_keys(password)
        login= WebDriverWait(driver, 30).until(EC.presence_of_element_located((By.XPATH, '/html/body/div[1]/div[1]/div[2]/c-wiz/div/div[3]/div/div[1]/div/div/button')))
        ActionChains(driver).move_to_element(login).click(login).perform()
    except (NoSuchElementException, TimeoutException, StaleElementReferenceException) as e:
         print("Already connected")
 

    
    return driver



def produce_dynamic_story_video(driver):
    template = """  
    {question}  

    🎭 Scene 1: [Brief, attention-grabbing opening]  
    ⚡ Scene 2: [Escalation or twist]  
    🎬 Scene 3: [Climax or big reveal]  
    🏁 Scene 4: [Quick resolution or cliffhanger]  
    """  

    agent_youtube=Agent(template)


    question = "Generate a creative story with engaging scenes and characters."
    
    response=agent_youtube.run(['question']).run(question=question)
    response = [x for i, x in enumerate(response.split("\n")) if i % 2 == 0]

    add = driver.find_element(By.XPATH, '/html/body/ytd-app/div[1]/div[2]/ytd-masthead/div[4]/div[3]/div[2]/ytd-button-renderer/yt-button-shape/button/yt-touch-feedback-shape/div/div[2]')
    add.click()
    ligne= driver.find_element(By.XPATH, '/html/body/ytd-app/ytd-popup-container/tp-yt-iron-dropdown/div/ytd-multi-page-menu-renderer/div[3]/div[1]/yt-multi-page-menu-section-renderer/div[2]/ytd-compact-link-renderer[1]/a/tp-yt-paper-item')
    max_attempts = 5
    attempt = 0
    success = False
    while not success and attempt < max_attempts:
        try:
            ligne = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, '/html/body/ytd-app/ytd-popup-container/tp-yt-iron-dropdown/div/ytd-multi-page-menu-renderer/div[3]/div[1]/yt-multi-page-menu-section-renderer/div[2]/ytd-compact-link-renderer[1]/a/tp-yt-paper-item'))
        )
            ActionChains(driver).move_to_element(ligne).click().perform()
            success = True
        except (NoSuchElementException, TimeoutException, StaleElementReferenceException) as e:
            print(f"Attempt {attempt + 1}: Failed to click on ligne element")
            attempt += 1
            time.sleep(1)

    try:
        chaine_new = driver.find_element(By.XPATH, '/html/body/ytd-app/ytd-popup-container/tp-yt-paper-dialog/ytd-channel-creation-dialog-renderer/div/div[6]/ytd-button-renderer[2]/yt-button-shape/button/yt-touch-feedback-shape/div/div[2]')
        chaine_new.click()
    except (NoSuchElementException, TimeoutException, StaleElementReferenceException) as e:
        print("chaine already exists")
    upload_video= driver.find_element(By.XPATH, '/html/body/ytcp-uploads-dialog/tp-yt-paper-dialog/div/ytcp-uploads-file-picker/div/input')


    audio_files, video_name, video_path = generate_video_with_audio(response)  
    
    upload_video.send_keys( video_path)
    os.remove(video_name)  # Remove temp video
    for audio_file in audio_files:
        os.remove(audio_file)  # Remove temp audio files

    max_attempts = 5
    attempt = 0
    title_textbox = None
    while attempt < max_attempts and title_textbox is None:
        try:
            title_textbox = driver.find_element(By.ID, 'textbox')
        except (NoSuchElementException, TimeoutException, StaleElementReferenceException) as e:
            print(f"Attempt {attempt + 1}: Title textbox not found. Retrying...")
            attempt += 1
            time.sleep(1)

    description_textbox=driver.find_element(By.XPATH, '/html/body/ytcp-uploads-dialog/tp-yt-paper-dialog/div/ytcp-animatable[1]/ytcp-ve/ytcp-video-metadata-editor/div/ytcp-video-metadata-editor-basics/div[2]/ytcp-video-description/div/ytcp-social-suggestions-textbox/ytcp-form-input-container/div[1]/div[2]/div/ytcp-social-suggestion-input/div')
    non_enfant=driver.find_element(By.XPATH, '/html/body/ytcp-uploads-dialog/tp-yt-paper-dialog/div/ytcp-animatable[1]/ytcp-ve/ytcp-video-metadata-editor/div/ytcp-video-metadata-editor-basics/div[5]/ytkc-made-for-kids-select/div[4]/tp-yt-paper-radio-group/tp-yt-paper-radio-button[2]/div[2]/ytcp-ve')
    non_enfant.click()
    template = """  
    I am an AI assistant specialized in generating a concise title and a one-sentence description from a story.  
    Please provide a JSON object with:  
    - **title**: A short, engaging title (max 1 phrase).  
    - **description**: A brief summary (max 1 sentence).  

    {context}  
    """  


    agent_make_title_desc=Agent(template)
    llm_chain2=agent_make_title_desc.run(["context"])
    response2 = llm_chain2.run(context="\n".join(response))
    new_response2=response2.replace("```", "").replace("json","")
    title_description=json.loads(new_response2)
    title, description = title_description['title'], title_description['description']
    title_textbox.send_keys(title)
    description_textbox.send_keys(description)
    time.sleep(10)
    suivant=driver.find_element(By.XPATH, '/html/body/ytcp-uploads-dialog/tp-yt-paper-dialog/div/ytcp-animatable[2]/div/div[2]/ytcp-button[2]/ytcp-button-shape/button/yt-touch-feedback-shape/div/div[2]')
    suivant.click()
    suivant_0=driver.find_element(By.XPATH, '/html/body/ytcp-uploads-dialog/tp-yt-paper-dialog/div/ytcp-animatable[2]/div/div[2]/ytcp-button[2]/ytcp-button-shape/button/yt-touch-feedback-shape/div/div[2]')
    suivant_0.click()
    suivant_01=driver.find_element(By.XPATH, '/html/body/ytcp-uploads-dialog/tp-yt-paper-dialog/div/ytcp-animatable[2]/div/div[2]/ytcp-button[2]/ytcp-button-shape/button/yt-touch-feedback-shape/div/div[2]')
    suivant_01.click()
    public=driver.find_element(By.XPATH, '/html/body/ytcp-uploads-dialog/tp-yt-paper-dialog/div/ytcp-animatable[1]/ytcp-uploads-review/div[2]/div[1]/ytcp-video-visibility-select/div[2]/tp-yt-paper-radio-group/tp-yt-paper-radio-button[3]/div[2]')
    public.click()
    enregistrer=driver.find_element(By.XPATH, '/html/body/ytcp-uploads-dialog/tp-yt-paper-dialog/div/ytcp-animatable[2]/div/div[2]/ytcp-button[3]/ytcp-button-shape/button/yt-touch-feedback-shape/div/div[2]')
    enregistrer.click()
    os.remove(video_name)
    os.remove(video_path)
    time.sleep(10)

def generate_video_with_audio(response):
    audio_files = []
    width, height = 1080, 1920
    video_name = "output_video.mp4"
    fps = 1  # Frames per second
    fourcc = cv2.VideoWriter_fourcc(*"mp4v")  # Codec
    video_writer = cv2.VideoWriter(video_name, fourcc, fps, (width, height))
    blank_img = np.zeros(shape=(height, width, 3), dtype=np.uint8)
    radius = 200
    w, h = width // 2, height // 2  # Center of the image
    video_writer.write(blank_img)
    for i, scene in enumerate(response):
        if len(scene) > 0:
            audio_file = f"scene_{i}.mp3"
            tts = gTTS(text=scene, lang="en", slow=False)
            
            
            random_color = np.random.randint(0, high=256, size=(3,))
            random_color = (int(random_color[0]), int(random_color[1]), int(random_color[2]))
            
            cv2.circle(blank_img, center=(w, h), radius=radius, color=random_color, thickness=5)
            video_writer.write(blank_img)
            
            tts.save(audio_file)
            audio_files.append(audio_file)
            
            radius = radius//2  

    video_writer.release()
    video_path = os.path.abspath(video_name)

    video_clip = VideoFileClip(video_path)

    audio_clips = [AudioFileClip(audio_file) for audio_file in audio_files]
    combined_audio = concatenate_audioclips(audio_clips)
    final_video = video_clip.set_audio(combined_audio)

    final_video_name = "final_output_video.mp4"

    final_video.write_videofile(final_video_name, codec="libx264")
    
    video_path = os.path.abspath(final_video_name)
    return audio_files,video_name,video_path

if __name__ :

    email = os.getenv("EMAIL")
    password = os.getenv("PASSWORD")
    base_url = os.getenv("BASE_URL")
    driver = authenticate_user(email, password, base_url)
    produce_dynamic_story_video(driver)
    driver.quit()

    
    