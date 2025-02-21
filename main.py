from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import torch
import io, base64
from PIL import Image
from diffusers import StableDiffusionPipeline
from langchain_community.llms import Ollama
from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain
import undetected_chromedriver as uc
import os
import threading
torch.cuda.empty_cache()
import numpy as np 
import cv2
os.environ["PYTORCH_CUDA_ALLOC_CONF"] = "expandable_segments:True"
from selenium.common.exceptions import NoSuchElementException, TimeoutException, StaleElementReferenceException
pipeline = StableDiffusionPipeline.from_pretrained(
    "stabilityai/stable-diffusion-2-1", torch_dtype=torch.float32
)
pipeline = pipeline.to('cpu')
# Initialize the WebDriver and other settings
email="azizwerghighi@gmail.com"
password="12312300aziz@A"
base_url = "https://www.youtube.com/"
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

driver = authenticate_user(email, password, base_url)
llm=Ollama(model="smollm:135m", base_url="http://localhost:11434")

template = """  
I am an AI assistant specialized in generating imaginative and dynamic stories. Each line represents a new scene in the unfolding narrative. Here is the randomly generated story:  

[Describe the opening setting and introduce the protagonist.]  
[Introduce a conflict or mystery that drives the story forward.]  

{question}
"""


QA_CHAIN_PROMPT = PromptTemplate(
        template=template,
        input_variables=[ "question" ],
        )
        
llm_chain = LLMChain(
            llm=llm, 
            prompt=QA_CHAIN_PROMPT, 
            callbacks=None, 
            verbose=True
        )
# Generate a creative story prompt
question = "Generate a creative story with engaging scenes and characters."
response = [x for i, x in enumerate(llm_chain.run(question=question).split("\n")) if i % 2 == 0]

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

images = []


for scene_descr in response:
    image=pipeline(prompt=scene_descr).images[0]
    images.append(image)

video_name = "output_video.mp4"
fps = 10  # Frames per second
height, width, _ = images[0].shape
fourcc = cv2.VideoWriter_fourcc(*"mp4v")  # Codec
video_writer = cv2.VideoWriter(video_name, fourcc, fps, (width, height))

# Write each image to the video
for img in images:
    frame = np.array(img)  # Convert PIL image to NumPy array
    frame = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)  # Convert to BGR (OpenCV format)
    video_writer.write(frame)

video_writer.release()
upload_video= driver.find_element(By.XPATH, '/html/body/ytcp-uploads-dialog/tp-yt-paper-dialog/div/ytcp-uploads-file-picker/div/ytcp-uploads-file-picker-animation/div/div[3]/div')
upload_video.send_keys(os.getcwd()+"\\"+video_name)
print(f"Video saved as {video_name}")


driver.quit()
    
    