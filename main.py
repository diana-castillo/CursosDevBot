import os
import requests
import asyncio
from discord import Client
'''from dotenv import load_dotenv'''
from discord_bot import DiscordBot
from bs4 import BeautifulSoup

class WebCrawler(DiscordBot):
     def __init__(self):
          # Hace llamar el constructor de DiscordBot
          super().__init__()

     async def get_response(self, run_seg_coroutine: bool) -> list:
          
          keyword = self.keyword_seg  if run_seg_coroutine else self.keyword_obt
          search = True
          courses = []
          page = 1

          while search:

                # Realiza la solicitud HTTP
               url = f'https://www.cursosdev.com/coupons?page={page}'
               response = requests.get(url)
               
               if response.status_code != 200:
                    print('La solicitud a la página ' + str(page) + ' no fue exitosa')
                    break

               soup = BeautifulSoup(response.content, 'html.parser')
               divs_courses = soup.find_all('div', class_='w-screen')
               div_free_courses = divs_courses[1]

               course_elements = div_free_courses.find_all('a', class_='c-card')
               expired_courses = div_free_courses.find_all('span', string='Expired')
               if not course_elements or len(expired_courses) == 20:
                    break 

               for element in course_elements:
                    expired = element.find('span', string='Expired')
                    title = element.find('h2').text.strip()
                    link = element.get('href')
                    
                    if not expired and keyword.lower() in title.lower():
                         courses.append({
                              'title': title,
                              'link': link
                         })
                         
                         if self.last_course in [None, link] and run_seg_coroutine:
                              if self.last_course == link: courses.pop()
                              search = False
                              break
               
               if search:
                    page += 1
                    await asyncio.sleep(1)
               
          if len(courses) and run_seg_coroutine:
               self.last_course = courses[0]['link']

          return courses
          

if __name__ == '__main__':

     # Carga las variables de entorno y
     # Crea el cliente de Discord
     '''load_dotenv()'''
     client: Client = WebCrawler()
     client.start_bot( token= os.getenv('TOKEN'), 
                       id_ch_seg = int(os.getenv('ID_CH_SEG')), 
                       id_ch_obt = int(os.getenv('ID_CH_OBT')))