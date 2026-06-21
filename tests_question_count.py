from services.embeddingService import EmbeddingService
from services.evaluationService import EvaluationService
from services.questionGenerator import QuestionGenerator


def test_question_generator_refills_after_dedupe():
    responses = iter([
        '{"questions":[{"question":"What is photosynthesis?","options":[],"answer":"A","explanation":"E","difficulty":"Easy","source_excerpt":"S"},{"question":"What is photosynthesis?","options":[],"answer":"A","explanation":"E","difficulty":"Easy","source_excerpt":"S"}]}',
        '{"questions":[{"question":"Which pigment absorbs light?","options":[],"answer":"Chlorophyll","explanation":"E","difficulty":"Easy","source_excerpt":"S"}]}',
        '{"questions":[{"question":"Where does photosynthesis occur?","options":[],"answer":"Chloroplasts","explanation":"E","difficulty":"Easy","source_excerpt":"S"}]}',
    ])

    def fake_llm(_prompt):
        return next(responses)

    embedding_service = EmbeddingService()
    generator = QuestionGenerator(
        embedding_service=embedding_service,
        evaluation_service=EvaluationService(embedding_service),
        llm_client=fake_llm,
    )

    questions = generator.generate(
        context_chunks=["Photosynthesis occurs in chloroplasts. Chlorophyll absorbs light."],
        question_type="Short Answer",
        num_questions=3,
        difficulty="Easy",
    )

    assert len(questions) == 3
    assert len({item["question"] for item in questions}) == 3
