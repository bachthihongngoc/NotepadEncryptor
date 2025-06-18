import re
class Segmenter:
  @staticmethod
  def split_text_into_segments(full_text):
        # Thay thế xuống dòng bằng dấu cách để đảm bảo nhất quán khi tách
        full_text = full_text.replace('\n', ' \n ')
        # Tách câu theo: kết thúc bằng dấu chấm, chấm hỏi, chấm than hoặc xuống dòng
        sentence_endings = re.compile(r'(?<=[.,!?\n])\s+')
        segments = sentence_endings.split(full_text.strip())

        # Loại bỏ các chuỗi rỗng hoặc chỉ chứa khoảng trắng
        segments = [segment.strip() for segment in segments if segment.strip()]

        return segments