from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from core.search.segment_utils import Segmenter

class TFIDFKeywordSearcher:
  def __init__(self, top_k=5, similarity_threshold=0.002):
    #số kết quả liên quan nhất được trả về: 5
    self.top_k = top_k
    self.similarity_threshold = similarity_threshold
    
  def search(self, keyword: str, full_text: str) -> list[dict]:
        if not keyword.strip():
            return []

        segments = Segmenter.split_text_into_segments(full_text)
        if not segments:
            return []

        corpus = segments + [keyword]

        vectorizer = TfidfVectorizer()
        tfidf_matrix = vectorizer.fit_transform(corpus)

        query_vec = tfidf_matrix[-1]
        doc_vecs = tfidf_matrix[:-1]

        similarities = cosine_similarity(doc_vecs, query_vec).flatten()

        results = [
            {
                "index": i,
                "text": segments[i],
                "score": similarities[i]
            }
            for i in range(len(segments))
            if similarities[i] >= self.similarity_threshold
        ]

        results = sorted(results, key=lambda x: x["score"], reverse=True)

        return results[:self.top_k]
    