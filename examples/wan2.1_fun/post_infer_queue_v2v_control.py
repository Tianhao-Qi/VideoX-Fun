import base64
import json
import time
import urllib.parse
import requests

def post_infer(
    generation_method, 
    length_slider, 
    url='http://127.0.0.1:7860', 
    POST_TOKEN="", 
    timeout=5,
    base_model_path="none",
    lora_model_path="none",
    lora_alpha_slider=0.55,
    prompt_textbox="A young woman with beautiful and clear eyes and blonde hair standing and white dress in a forest wearing a crown. She seems to be lost in thought, and the camera focuses on her face. The video is of high quality, and the view is very clear. High quality, masterpiece, best quality, highres, ultra-detailed, fantastic.",
    negative_prompt_textbox="色调艳丽，过曝，静态，细节模糊不清，字幕，风格，作品，画作，画面，静止，整体发灰，最差质量，低质量，JPEG压缩残留，丑陋的，残缺的，多余的手指，画得不好的手部，画得不好的脸部，畸形的，毁容的，形态畸形的肢体，手指融合，静止不动的画面，杂乱的背景，三条腿，背景人很多，倒着走",
    sampler_dropdown="Flow",
    sample_step_slider=50,
    width_slider=672,
    height_slider=384,
    cfg_scale_slider=6,
    seed_textbox=43,
    control_video=None
):
    if control_video:
        try:
            if not control_video.startswith("http"):
                with open(control_video, "rb") as file:
                    video_data = file.read()

                control_video = base64.b64encode(video_data).decode('utf-8')
        except Exception as e:
            print(f"Error processing control_video: {e}")
            raise

    # Prepare the data payload
    datas = json.dumps({
        "base_model_path": base_model_path,
        "lora_model_path": lora_model_path,
        "lora_alpha_slider": lora_alpha_slider,
        "prompt_textbox": prompt_textbox,
        "negative_prompt_textbox": negative_prompt_textbox,
        "sampler_dropdown": sampler_dropdown,
        "sample_step_slider": sample_step_slider,
        "width_slider": width_slider,
        "height_slider": height_slider,
        "generation_method": generation_method,
        "length_slider": length_slider,
        "cfg_scale_slider": cfg_scale_slider,
        "seed_textbox": seed_textbox,
        "control_video": control_video
    })

    # Initialize session and set headers
    session = requests.session()
    session.headers.update({"Authorization": POST_TOKEN})

    # Send POST request
    post_r = session.post(f'{url}/videox_fun/infer_forward', data=datas, timeout=timeout)

    # Extract request ID from POST response headers
    request_id = post_r.headers.get("X-Eas-Queueservice-Request-Id")

    # Prepare query parameters for GET request
    query = {
        '_index_': '0',
        '_length_': '1',
        '_timeout_': str(timeout),
        '_raw_': 'false',
        '_auto_delete_': 'true',
    }
    if request_id:
        query['requestId'] = request_id

    query_str = urllib.parse.urlencode(query)

    # Polling GET request until status code is not 204
    status_code = 204
    while status_code == 204:
        if query_str:
            get_r = session.get(f'{url}/sink?{query_str}', timeout=timeout)
        else:
            get_r = session.get(f'{url}/sink', timeout=timeout)
        status_code = get_r.status_code
    # Decode and return the response content
    data = get_r.content.decode('utf-8')
    return data


if __name__ == '__main__':
    # initiate time
    time_start = time.time()  

    # EAS队列配置
    EAS_URL = 'http://17xxxxxxxxx.pai-eas.aliyuncs.com/api/predict/xxxxxxxx'
    # Use in EAS Queue
    TOKEN   = 'xxxxxxxx'
        
    # "Video Generation" and "Image Generation"
    generation_method = "Video Generation"
    # Video length
    length_slider = 81
    # Used in Lora models
    lora_model_path = "none"
    lora_alpha_slider = 0.55
    # Prompts
    prompt_textbox = "在这个阳光明媚的户外花园里，美女身穿一袭及膝的白色无袖连衣裙，裙摆在她轻盈的舞姿中轻柔地摆动，宛如一只翩翩起舞的蝴蝶。阳光透过树叶间洒下斑驳的光影，映衬出她柔和的脸庞和清澈的眼眸，显得格外优雅。仿佛每一个动作都在诉说着青春与活力，她在草地上旋转，裙摆随之飞扬，仿佛整个花园都因她的舞动而欢愉。周围五彩缤纷的花朵在微风中摇曳，玫瑰、菊花、百合，各自释放出阵阵香气，营造出一种轻松而愉快的氛围。"
    negative_prompt_textbox = "色调艳丽，过曝，静态，细节模糊不清，字幕，风格，作品，画作，画面，静止，整体发灰，最差质量，低质量，JPEG压缩残留，丑陋的，残缺的，多余的手指，画得不好的手部，画得不好的脸部，畸形的，毁容的，形态畸形的肢体，手指融合，静止不动的画面，杂乱的背景，三条腿，背景人很多，倒着走"
    # Sampler name
    sampler_dropdown = "Flow"
    # Sampler steps
    sample_step_slider = 50
    # height and width 
    width_slider = 480
    height_slider = 832
    # cfg scale
    cfg_scale_slider = 6
    seed_textbox = 43

    # 控制视频路径（可以是本地路径或 URL）
    control_video_path = "asset/000000.mp4"  # 替换为实际的视频路径

    outputs = post_infer(
        generation_method, 
        length_slider, 
        lora_model_path=lora_model_path,
        lora_alpha_slider=lora_alpha_slider,
        prompt_textbox=prompt_textbox,
        negative_prompt_textbox=negative_prompt_textbox,
        sampler_dropdown=sampler_dropdown,
        sample_step_slider=sample_step_slider,
        width_slider=width_slider,
        height_slider=height_slider,
        cfg_scale_slider=cfg_scale_slider,
        seed_textbox=seed_textbox,
        url=EAS_URL, 
        POST_TOKEN=TOKEN,
        control_video=control_video_path  # 传递控制视频路径
    )
    # Get decoded data
    outputs = json.loads(base64.b64decode(json.loads(outputs)[0]['data']))
    base64_encoding = outputs["base64_encoding"]
    decoded_data = base64.b64decode(base64_encoding)

    is_image = True if generation_method == "Image Generation" else False
    if is_image or length_slider == 1:
        file_path = "1.png"
    else:
        file_path = "1.mp4"
    with open(file_path, "wb") as file:
        file.write(decoded_data)
        
    # End of record time
    # The calculated time difference is the execution time of the program, expressed in seconds / s
    time_end = time.time()  
    time_sum = (time_end - time_start)
    print('# --------------------------------------------------------- #')
    print(f'#   Total expenditure: {time_sum}s')
    print('# --------------------------------------------------------- #')
