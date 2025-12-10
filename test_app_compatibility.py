"""
Unit tests for app.py backwards compatibility layer.

Tests the transformation from HOTDOG's modern format to legacy frontend format.
"""

import sys
import os

# Add parent directory to path so we can import app
sys.path.insert(0, os.path.dirname(__file__))

from app import _transform_to_legacy_format


def test_transform_basic_structure():
    """Test basic structure transformation with one section and one question."""
    hotdog_output = {
        'sections': [
            {
                'section_id': 'general_info',
                'section_name': 'General Project Information',
                'description': 'Basic project details',
                'questions': [
                    {
                        'question_id': 'Q1',
                        'question_text': 'What is the project name?',
                        'has_answer': True,
                        'primary_answer': {
                            'text': 'CIPP Rehabilitation Project - Main Street',
                            'pages': [1, 2],
                            'confidence': 0.95
                        }
                    }
                ]
            }
        ],
        'document_name': 'test.pdf',
        'total_pages': 50,
        'questions_answered': 1,
        'total_questions': 105
    }

    result = _transform_to_legacy_format(hotdog_output)

    # Verify top-level structure
    assert 'sections' in result
    assert len(result['sections']) == 1
    assert result['document_name'] == 'test.pdf'
    assert result['total_pages'] == 50

    # Verify section structure
    section = result['sections'][0]
    assert section['section_name'] == 'General Project Information'
    assert section['section_id'] == 'general_info'
    assert 'questions' in section
    assert len(section['questions']) == 1

    # Verify question transformation
    question = section['questions'][0]
    assert question['question_id'] == 'Q1'
    assert question['question'] == 'What is the project name?'  # question_text → question
    assert question['answer'] == 'CIPP Rehabilitation Project - Main Street'  # primary_answer.text → answer
    assert question['page_citations'] == [1, 2]  # primary_answer.pages → page_citations
    assert question['confidence'] == 0.95

    print("[PASS] test_transform_basic_structure")


def test_transform_unanswered_question():
    """Test transformation of unanswered questions."""
    hotdog_output = {
        'sections': [
            {
                'section_id': 'materials',
                'section_name': 'Materials',
                'description': 'Material specs',
                'questions': [
                    {
                        'question_id': 'Q11',
                        'question_text': 'What resin type is required?',
                        'has_answer': False,
                        'primary_answer': None
                    }
                ]
            }
        ],
        'document_name': 'test.pdf',
        'total_pages': 50,
        'questions_answered': 0,
        'total_questions': 105
    }

    result = _transform_to_legacy_format(hotdog_output)

    question = result['sections'][0]['questions'][0]
    assert question['question'] == 'What resin type is required?'
    assert question['answer'] is None
    assert question['page_citations'] == []
    assert question['confidence'] == 0.0

    print("[PASS] test_transform_unanswered_question PASSED")


def test_transform_multiple_sections():
    """Test transformation with multiple sections and questions."""
    hotdog_output = {
        'sections': [
            {
                'section_id': 'general',
                'section_name': 'General',
                'description': 'General info',
                'questions': [
                    {
                        'question_id': 'Q1',
                        'question_text': 'Question 1?',
                        'has_answer': True,
                        'primary_answer': {
                            'text': 'Answer 1',
                            'pages': [1],
                            'confidence': 0.9
                        }
                    },
                    {
                        'question_id': 'Q2',
                        'question_text': 'Question 2?',
                        'has_answer': True,
                        'primary_answer': {
                            'text': 'Answer 2',
                            'pages': [2, 3],
                            'confidence': 0.85
                        }
                    }
                ]
            },
            {
                'section_id': 'materials',
                'section_name': 'Materials',
                'description': 'Material specs',
                'questions': [
                    {
                        'question_id': 'Q11',
                        'question_text': 'Question 11?',
                        'has_answer': False,
                        'primary_answer': None
                    }
                ]
            }
        ],
        'document_name': 'test.pdf',
        'total_pages': 50,
        'questions_answered': 2,
        'total_questions': 105
    }

    result = _transform_to_legacy_format(hotdog_output)

    assert len(result['sections']) == 2
    assert len(result['sections'][0]['questions']) == 2
    assert len(result['sections'][1]['questions']) == 1

    # Verify first section, first question
    q1 = result['sections'][0]['questions'][0]
    assert q1['question'] == 'Question 1?'
    assert q1['answer'] == 'Answer 1'
    assert q1['page_citations'] == [1]

    # Verify first section, second question
    q2 = result['sections'][0]['questions'][1]
    assert q2['question'] == 'Question 2?'
    assert q2['answer'] == 'Answer 2'
    assert q2['page_citations'] == [2, 3]

    # Verify second section, unanswered question
    q11 = result['sections'][1]['questions'][0]
    assert q11['question'] == 'Question 11?'
    assert q11['answer'] is None
    assert q11['page_citations'] == []

    print("[PASS] test_transform_multiple_sections PASSED")


def test_transform_empty_sections():
    """Test transformation with empty sections array."""
    hotdog_output = {
        'sections': [],
        'document_name': 'test.pdf',
        'total_pages': 0,
        'questions_answered': 0,
        'total_questions': 0
    }

    result = _transform_to_legacy_format(hotdog_output)

    assert result['sections'] == []
    assert result['document_name'] == 'test.pdf'
    assert result['total_pages'] == 0

    print("[PASS] test_transform_empty_sections PASSED")


def test_transform_missing_optional_fields():
    """Test transformation handles missing optional fields gracefully."""
    hotdog_output = {
        'sections': [
            {
                'section_name': 'Test Section',
                'questions': [
                    {
                        'question_text': 'Test Question?',
                        'has_answer': True,
                        'primary_answer': {
                            'text': 'Test Answer'
                            # Missing 'pages' and 'confidence'
                        }
                    }
                ]
            }
        ]
        # Missing metadata fields
    }

    result = _transform_to_legacy_format(hotdog_output)

    assert result['document_name'] == ''
    assert result['total_pages'] == 0
    assert result['sections'][0]['section_id'] == ''
    assert result['sections'][0]['questions'][0]['page_citations'] == []
    assert result['sections'][0]['questions'][0]['confidence'] == 0.0

    print("[PASS] test_transform_missing_optional_fields PASSED")


if __name__ == '__main__':
    print("\n" + "="*70)
    print("RUNNING BACKWARDS COMPATIBILITY TRANSFORMATION TESTS")
    print("="*70 + "\n")

    try:
        test_transform_basic_structure()
        test_transform_unanswered_question()
        test_transform_multiple_sections()
        test_transform_empty_sections()
        test_transform_missing_optional_fields()

        print("\n" + "="*70)
        print("[PASS] ALL TESTS PASSED")
        print("="*70 + "\n")
    except AssertionError as e:
        print("\n" + "="*70)
        print(f"[FAIL] TEST FAILED: {e}")
        print("="*70 + "\n")
        sys.exit(1)
    except Exception as e:
        print("\n" + "="*70)
        print(f"[FAIL] UNEXPECTED ERROR: {e}")
        print("="*70 + "\n")
        sys.exit(1)
