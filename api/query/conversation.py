from fastapi import APIRouter
from fastapi import HTTPException
import random


from api.models.conversation import Conversation
from api.database.models import ConversationsDB
from api.database.database import session
from api.database.crud import get_user_by_email


router = APIRouter(prefix="/conversation")


@router.post("/save", status_code=200)
def save(conversation: Conversation, conversation_id: int = None):
    user = get_user_by_email(conversation.messages[0].current_user.email)
    conversations = []
    if conversation is None:
        conversation_id = random.randint(0, 1000000000000)
    for message in conversation.messages:
        message_db = ConversationsDB(
            user_id=user.id,
            conversation_id=conversation_id,
            message=message.text,
            is_user_message=message.is_user_message,
        )
        conversations.append(message_db)

    if len(conversations) > 0:
        try:
            session.bulk_save_objects(conversations)
            session.commit()
        except Exception as e:
            print(e)
            session.rollback()
            raise HTTPException(
                status_code=400, detail=f"Could not save conversation to database. {e}"
            )
        finally:
            session.close()
            session.remove()
    else:
        return conversations
