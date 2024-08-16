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

# 6 Define priority only to be 1 and 2

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


    # applicant_id: int | None = Field(default=None, foreign_key="applicant.id", primary_key=True)
    # position_id: int | None = Field(default=None, foreign_key="position.id", primary_key=True)


    # position_1: PositionChoice | None = None
    # position_2: PositionChoice | None = None
    
    # @model_validator(mode="before")
    # def validate_and_normalize_positions(cls, values):
    #     pos1 = values.get("position_1")
    #     pos2 = values.get("position_2")
        
    #     # Title-case the positions
    #     if pos1:
    #         values["position_1"] = pos1.title()
    #     if pos2:
    #         values["position_2"] = pos2.title()
        
    #     # If both positions are the same, set position_2 to None
    #     if pos1 and pos2 and pos1 == pos2:
    #         values["position_2"] = None
        
    #     return values   



    
while True:
    try:
        conn = psycopg2.connect(host='localhost', database='voting_fastapi',user='postgres',
                                password='root',cursor_factory=RealDictCursor)
        cursor = conn.cursor()
        print('Database connection was successful')
        break
    except Exception as error:
        print("Connecting to database failed")
        print("Error:", error)
        time.sleep(2)


post_applicants = [{
   "fname": "Nolan",
   "lname": "John",
   "email": "nolan@gmail.com",
   "position": "President",
   "status": "pending",
   "published": False,
   "department":"Health",
   "experience":[
       {'title': "representative", "description": "two years working at IT"}
       ]}, 
]   

    
    applicant = Applicant(fname=applicant_data.fname, 
                        lname=applicant_data.lname, 
                        email=applicant_data.email, 
                        position=applicant_data.position, 
                        status=applicant_data.status, 
                        published=applicant_data.published,
                        department=applicant_data.department,
                        # disabled=applicant_data.disabled,
                        created_at=datetime.now(timezone.utc))





       cursor.execute("""SELECT * FROM applicants WHERE id = %s""", str(applicant_id))
    applicant = cursor.fetchone()
    if applicant is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"The applicant with id {applicant_id} is not found")
    return {"applicant_detail": applicant}


     cursor.execute("""SELECT * FROM applicants""")
    applicants = cursor.fetchall()
    return {"message": applicants}


    cursor.execute("""UPDATE applicants SET status = %s, published = %s WHERE id = %s RETURNING*""",
                    (applicant.status, applicant.published, str(applicant_id)))
    updated_applicant = cursor.fetchone()
    conn.commit()
    if updated_applicant is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"The applican with id {applicant_id} is not found")
    return {"data": updated_applicant}


    applicant = Applicant(fname=updated_applicant.fname, 
                    lname=updated_applicant.lname, 
                    email=updated_applicant.email, 
                    position=updated_applicant.position, 
                    status=updated_applicant.status, 
                    published=updated_applicant.published,
                    department=updated_applicant.department,
                    # disabled=updated_applicant.disabled,
                    created_at=datetime.now(timezone.utc))


    cursor.execute("""DELETE FROM applicants WHERE id = %s returning *""", (applicant_id,))
    deleted_applicant = cursor.fetchone()
    conn.commit()
    if deleted_applicant is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"The applicant with id {applicant_id} is not found")
    return Response(status_code=status.HTTP_204_NO_CONTENT)