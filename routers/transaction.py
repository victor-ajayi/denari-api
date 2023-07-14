from fastapi import APIRouter, Depends, HTTPException, Response, status
from sqlalchemy.orm import Session

from app import models, oauth2, schemas
from app.database import get_db
from app.services import transaction as transaction_service

router = APIRouter(prefix="/transactions", tags=["Transactions"])


@router.post("/", status_code=status.HTTP_201_CREATED)
def create_transaction(
    transaction_create: schemas.TransactionCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(oauth2.get_current_user),
) -> schemas.Transaction:
    """Create transaction"""

    return transaction_service.create(current_user.id, transaction_create, db)


@router.get("/{id}", status_code=200)
def get_transaction(
    id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(oauth2.get_current_user),
) -> schemas.Transaction:
    """Gets an account transaction"""

    return transaction_service.get_transaction(current_user.id, id, db)


@router.get("/", status_code=200)
def get_all_transactions(
    account_id: int | None = None,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(oauth2.get_current_user),
) -> list[schemas.Transaction]:
    """Get all transactions

    Returns:
    - All transactions for an account if account_id is passed
    - All user transactions if account_id is not passed

    """

    if account_id:
        return transaction_service.get_account_transactions(
            current_user.id, account_id, db
        )

    return transaction_service.get_all_transactions(current_user.id, db)


@router.patch("/{id}", status_code=200)
def update_transaction(
    id: int,
    transaction_update: schemas.TransactionUpdate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(oauth2.get_current_user),
) -> schemas.Transaction:
    """Update account transaction"""

    transaction = transaction_service.get_transaction(current_user.id, id, db)

    if transaction.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to perform action.",
        )

    if transaction.amount != transaction_update.amount:
        transaction = transaction_service.update(
            current_user.id, id, transaction_update, db
        )

    return transaction


@router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_transaction(
    id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(oauth2.get_current_user),
):
    """Delete account transaction"""

    transaction = transaction_service.get_transaction(current_user.id, id, db)

    if transaction.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to perform action.",
        )

    transaction = transaction_service.delete(current_user.id, id, db)

    return Response(status_code=status.HTTP_204_NO_CONTENT)
