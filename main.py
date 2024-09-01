# 导入FastAPI类
from fastapi import FastAPI,Body,status
from fastapi.responses import JSONResponse, Response
from typing import Union
import time
import os
import json
import random
import uvicorn
from distutils.util import strtobool
from log import new_logger

path = os.getcwd()
hitokoto_data = []
config = json.load(open('./config.json', 'r', encoding='utf8'))

def get_hitokoto_count():
    return len(hitokoto_data)

def reponse(*, code=200,data: Union[list, dict, str],message="Success",hitokoto="") -> Response:
    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content={
            'code': code,
            'message': message,
            'data': data
        }
    )

# 使用当前模块的名称构建FastAPI app
app = FastAPI()

logger = new_logger('HITOKOTO-MAIN', False)
@app.get("/HITOKOTO", response_class=JSONResponse)
async def get_hitokoto_result(data:str="json"):
    hitokoto_count = get_hitokoto_count()
    if hitokoto_count>0:
        radom_hitokoto = random.randint(0,hitokoto_count-1)
        hitokoto_result = hitokoto_data[radom_hitokoto]
        hitokoto_str = hitokoto_result['hitokoto']
        if data == "text":
            hitokoto_result = hitokoto_str
        logger.info(hitokoto_str)
        return reponse(data=hitokoto_result,code=200,message="success")
    else:
        _msg = "未读取到一言，即将重新读取"
        logger.warn(_msg)
        print(_msg)
        init_hitokoto()
        return reponse(data={'msg':_msg},code=500,message="error")

def init_hitokoto():
    # 遍历sentences文件夹
    for root, dirs, files in os.walk(f'{path}\sentences'):
        for file in files:
            # 检查文件扩展名，读取文件
            if file.endswith('.json'):
                file_path = os.path.join(root, file)
                logger.info(f"正在读取文件: {file_path}")

                # 使用open函数读取文件内容
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:  # 指定编码为utf-8，以防乱码
                        _json = json.load(f)
                        # 添加已读取的hitokoto数据
                        for _data in _json:
                            # 添加数据到集合内
                            hitokoto_data.append(_data)
                        logger.info(f"读取文件{file_path}完成")
                except Exception as e:
                    logger.info(f"读取文件{file_path}时出错: {e}")
    hitokoto_count = get_hitokoto_count()
    logger.info(f"成功读取{hitokoto_count}条一言")

if __name__ == '__main__':
    start = time.time()
    init_hitokoto()
    logger.info(f"HITOKOTO初始化耗时：{time.time() - start}")
    uvicorn.run(app, host=int(config['host']), port=int(config['port']),access_log=strtobool(config['api_log']))
