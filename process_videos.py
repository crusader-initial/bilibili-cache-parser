import os
import json
import subprocess
from pathlib import Path

def process_videos(base_path):
    video_path = Path(base_path) / 'video'
    for video_dir in video_path.iterdir():
        if not video_dir.is_dir():
            continue
            
        sub_dirs = [d for d in video_dir.iterdir() if d.is_dir()]
        if not sub_dirs:
            continue
        
        cache_dir = sub_dirs[0]
        
        # 读取entry.json获取标题
        entry_json_path = cache_dir / 'entry.json'
        if not entry_json_path.exists():
            print(f"找不到entry.json: {entry_json_path}")
            continue
            
        try:
            with open(entry_json_path, 'r', encoding='utf-8') as f:
                entry_data = json.load(f)
                title = entry_data.get('title', 'unknown')
                title = "".join(c for c in title if c.isalnum() or c in (' ', '-', '_'))
                
                # 重命名视频文件夹
                new_video_dir = video_dir.parent / title
                try:
                    video_dir.rename(new_video_dir)
                    video_dir = new_video_dir  # 更新文件夹路径
                    cache_dir = next(d for d in video_dir.iterdir() if d.is_dir())  # 更新cache_dir路径
                except Exception as e:
                    print(f"重命名文件夹失败: {e}")
        except Exception as e:
            print(f"读取entry.json失败: {e}")
            continue
            
        # 查找音视频文件
        audio_file = None
        video_file = None
        item_dir = None
        
        for d in cache_dir.iterdir():
            if d.is_dir():
                item_dir = d
                audio_path = item_dir / 'audio.m4s'
                video_path = item_dir / 'video.m4s'
                
                if audio_path.exists():
                    audio_file = audio_path
                if video_path.exists():
                    video_file = video_path
                break
        
        if not audio_file or not video_file:
            print(f"找不到音频或视频文件: {cache_dir}")
            continue
            
        # 直接在item_dir中生成mp4文件
        output_file = item_dir / f"{title}.mp4"
        
        # 使用ffmpeg合并音视频
        try:
            cmd = [
                'ffmpeg',
                '-i', str(video_file),
                '-i', str(audio_file),
                '-c', 'copy',
                str(output_file)
            ]
            subprocess.run(cmd, check=True)
            print(f"成功生成视频: {output_file}")
        except subprocess.CalledProcessError as e:
            print(f"合并视频失败: {e}")

if __name__ == "__main__":
    # 使用当前目录作为基础路径
    base_path = os.path.dirname(os.path.abspath(__file__))
    print(base_path)
    process_videos(base_path)