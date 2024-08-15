# 1. SELECTION LOGIC
#consider experience  +5 and 1st priority +5
def determine_winner(applicants):
    # Sort applicants by score, then by priority (1 takes precedence over 2)
    applicants.sort(key=lambda x: (x['score'], x['priority']), reverse=True)

    # Handle tie scenarios
    top_applicants = [app for app in applicants if app['score'] == applicants[0]['score']]
    
    if len(top_applicants) > 1:
        # If tied and priorities match, check experience
        for app in top_applicants:
            if app['priority'] == 1 and app['experience'] > max(app['experience'] for app in top_applicants if app['priority'] == 1):
                app['score'] += 5
    
    # Re-sort after experience adjustment
    applicants.sort(key=lambda x: (x['score'], x['priority']), reverse=True)
    
    return applicants[0]  # Return the applicant with the highest score and priority



# 5. if the status changes:
# 1) from default pending to approved then published will turn to public
# 2) from default or any other to reject then published turns to private, and disable the applicant...



# 3. limit user can only vote five application no matter it is first priority or second. -> votes

user_votes = session.exec(
    select(Vote)
    .where(Vote.user_id == some_user_id)
    .join(Vote.applicant_position)
).all()

votes_count = session.exec(
    select(func.count(Vote.id))
    .join(ApplicantPosition)
    .where(ApplicantPosition.applicant_id == some_applicant_id)
    .where(ApplicantPosition.position_id == some_position_id)
).scalar()


@router.post("/votes")
async def cast_vote(applicant_position_id: int, user_id: int, vote_dir: int, session: Session = Depends(get_session)):
    user = session.get(User, user_id)
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    
    existing_votes = session.query(Vote).filter(Vote.user_id == user_id).all()
    if len(existing_votes) >= 5:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="You can only vote up to five positions.")
    
    # Check if the user has already voted for this position
    existing_vote = session.query(Vote).filter(
        Vote.user_id == user_id, 
        Vote.applicant_position_id == applicant_position_id
    ).first()
    if existing_vote:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="You have already voted for this position.")
    
    # Create and add the new vote
    new_vote = Vote(applicant_position_id=applicant_position_id, user_id=user_id, dir=vote_dir)
    session.add(new_vote)
    session.commit()
    return {"message": "Vote cast successfully"}



# 2. Done the post part. still needs to do patch part. limit 2 positions - applicant

@router.post("/applicants", status_code=status.HTTP_201_CREATED, response_model=Applicant)
@router.patch("/applicants/{applicant_id}", response_model=Applicant)


# Done 4. if user is applicant  -> user  
# @property



