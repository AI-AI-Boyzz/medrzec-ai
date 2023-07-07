from google.cloud import language_v1


def sample_analyze_sentiment(content: str) -> int:
    client = language_v1.LanguageServiceClient()

    type_ = language_v1.Document.Type.PLAIN_TEXT
    document = {"type_": type_, "content": content}
    response = client.analyze_sentiment(request={"document": document})
    sentiment = response.document_sentiment

    return sentiment.score
