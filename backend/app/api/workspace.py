import uuid
from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.database.session import get_db
from app.services.auth_service import get_current_user
from app.models.user import User
from app.models.saas import Workspace, WorkspaceMember, Comment, ActivityLog
from pydantic import BaseModel

router = APIRouter(prefix="/workspace", tags=["Team Collaboration"])

class WorkspaceCreate(BaseModel):
    name: str

class InviteMember(BaseModel):
    email: str
    role: str = "member"  # admin, member, viewer

class CommentCreate(BaseModel):
    result_id: uuid.UUID
    message: str

@router.post("", status_code=status.HTTP_201_CREATED)
async def create_workspace(
    ws_in: WorkspaceCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    # Create workspace
    workspace = Workspace(name=ws_in.name, owner_id=current_user.id)
    db.add(workspace)
    await db.commit()
    await db.refresh(workspace)

    # Add owner as workspace member
    owner_member = WorkspaceMember(
        workspace_id=workspace.id,
        user_id=current_user.id,
        role="owner",
        status="active"
    )
    db.add(owner_member)
    
    # Log Activity
    log = ActivityLog(
        user_id=current_user.id,
        description=f"Created workspace '{ws_in.name}'",
        category="team"
    )
    db.add(log)
    await db.commit()
    
    return workspace

@router.post("/{workspace_id}/invite", status_code=status.HTTP_200_OK)
async def invite_team_member(
    workspace_id: uuid.UUID,
    invite_in: InviteMember,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    # Verify workspace ownership
    result = await db.execute(
        select(WorkspaceMember).filter(
            WorkspaceMember.workspace_id == workspace_id,
            WorkspaceMember.user_id == current_user.id
        )
    )
    membership = result.scalars().first()
    if not membership or membership.role not in ["owner", "admin"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Unauthorized. Only Owners or Admins can invite team members."
        )

    # Find user by email
    user_result = await db.execute(select(User).filter(User.email == invite_in.email))
    invitee = user_result.scalars().first()
    if not invitee:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User email not found in Reel Truth Checker directory."
        )

    # Add membership row
    new_member = WorkspaceMember(
        workspace_id=workspace_id,
        user_id=invitee.id,
        role=invite_in.role,
        status="invited"
    )
    db.add(new_member)
    
    log = ActivityLog(
        user_id=current_user.id,
        description=f"Invited {invite_in.email} to workspace",
        category="team"
    )
    db.add(log)
    await db.commit()
    
    return {"status": "invited", "email": invite_in.email}

@router.get("/{workspace_id}/members", status_code=status.HTTP_200_OK)
async def list_members(
    workspace_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    # Verify requester belongs to workspace
    result = await db.execute(
        select(WorkspaceMember).filter(
            WorkspaceMember.workspace_id == workspace_id,
            WorkspaceMember.user_id == current_user.id
        )
    )
    membership = result.scalars().first()
    if not membership:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied."
        )

    members_result = await db.execute(
        select(WorkspaceMember, User.email)
        .join(User, WorkspaceMember.user_id == User.id)
        .filter(WorkspaceMember.workspace_id == workspace_id)
    )
    
    formatted_members = []
    for row in members_result.all():
        m, email = row
        formatted_members.append({
            "member_id": m.id,
            "user_id": m.user_id,
            "email": email,
            "role": m.role,
            "status": m.status
        })
    return formatted_members

@router.post("/comments", status_code=status.HTTP_201_CREATED)
async def post_comment(
    comm_in: CommentCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    comment = Comment(
        result_id=comm_in.result_id,
        user_id=current_user.id,
        message=comm_in.message
    )
    db.add(comment)
    await db.commit()
    await db.refresh(comment)
    return comment

@router.post("/comments/{comment_id}/resolve", status_code=status.HTTP_200_OK)
async def resolve_comment(
    comment_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    result = await db.execute(select(Comment).filter(Comment.id == comment_id))
    comment = result.scalars().first()
    if not comment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Comment not found"
        )
        
    comment.is_resolved = not comment.is_resolved
    await db.commit()
    return {"comment_id": comment.id, "is_resolved": comment.is_resolved}
