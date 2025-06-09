from sqlalchemy.orm import Session
from sqlalchemy import text
from typing import Optional, Dict, Any
from app.models.user import Wallet, WalletTransaction


class WalletService:
    
    @staticmethod
    def process_transaction(
        db: Session,
        wallet_id: int,
        transaction_type: str,
        amount: float,
        source: str,
        remark: Optional[str] = None,
        additional_info: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Process a wallet transaction using stored procedures.
        
        Credit transactions: Add amount to fixed_balance
        Debit transactions: Deduct from monthly_balance first, then fixed_balance
        
        Args:
            db: Database session
            wallet_id: ID of the wallet
            transaction_type: 'credit' or 'debit'
            amount: Transaction amount
            source: Source of the transaction
            remark: Optional remark
            additional_info: Optional additional information
            
        Returns:
            Dictionary with transaction details
        """
        try:
            # Validate transaction type
            if transaction_type.lower() not in ['credit', 'debit']:
                return {"success": False, "error": "Invalid transaction type. Must be 'credit' or 'debit'"}
            
            # Validate amount
            if amount <= 0:
                return {"success": False, "error": "Amount must be greater than 0"}
            
            # Call the stored procedure
            result = db.execute(
                text("SELECT process_wallet_transaction(:wallet_id, :transaction_type, :amount, :source, :remark, :additional_info)"),
                {
                    "wallet_id": wallet_id,
                    "transaction_type": transaction_type.lower(),
                    "amount": amount,
                    "source": source,
                    "remark": remark,
                    "additional_info": additional_info
                }
            )
            
            transaction_id = result.scalar()
            
            # Commit the transaction
            db.commit()
            
            # Get the created transaction details
            transaction = db.query(WalletTransaction).filter(
                WalletTransaction.transaction_id == transaction_id
            ).first()
            
            # Get updated wallet details
            wallet = db.query(Wallet).filter(
                Wallet.wallet_id == wallet_id
            ).first()
            
            if transaction and wallet:
                return {
                    "success": True,
                    "transaction_id": transaction_id,
                    "wallet_id": wallet_id,
                    "transaction_type": transaction.transaction_type,
                    "amount": transaction.amount,
                    "previous_balance": transaction.previous_balance,
                    "current_balance": transaction.current_balance,
                    "wallet_monthly_balance": wallet.monthly_balance,
                    "wallet_fixed_balance": wallet.fixed_balance,
                    "wallet_total_balance": wallet.monthly_balance + wallet.fixed_balance,
                    "source": transaction.source,
                    "remark": transaction.remark,
                    "additional_info": transaction.additional_info,
                    "updated_at": transaction.updated_at
                }
            else:
                return {"success": False, "error": "Transaction or wallet not found after processing"}
                
        except Exception as e:
            db.rollback()
            return {"success": False, "error": str(e)}
    
    @staticmethod
    def get_wallet_balance(db: Session, wallet_id: int) -> Dict[str, Any]:
        """Get wallet balance details."""
        try:
            result = db.execute(
                text("SELECT * FROM get_wallet_balance(:wallet_id)"),
                {"wallet_id": wallet_id}
            )
            
            balance_info = result.fetchone()
            
            if balance_info:
                return {
                    "success": True,
                    "wallet_id": balance_info[0],
                    "monthly_balance": balance_info[1],
                    "fixed_balance": balance_info[2],
                    "total_balance": balance_info[3]
                }
            else:
                return {"success": False, "error": "Wallet not found"}
                
        except Exception as e:
            return {"success": False, "error": str(e)}