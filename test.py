# SELECTION LOGIC

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


# limit 2 positions

def apply_for_position(applicant_id, new_position):
    current_positions = get_positions_for_applicant(applicant_id)
    if len(current_positions) >= 2:
        raise ValueError("An applicant can only apply for two positions.")
    add_position(applicant_id, new_position)

    def validate_positions_limit(session: Session, applicant_id: int, new_positions: list[PositionChoice]):
    current_positions_count = session.query(ApplicantPosition).filter_by(applicant_id=applicant_id).count()
    if current_positions_count + len(new_positions) > 2:
        raise ValueError("An applicant can only apply for a maximum of two positions.")


@router.post("/applicants", status_code=status.HTTP_201_CREATED, response_model=Applicant)
async def create_applicant(applicant_data: ApplicantCreate, session: Session = Depends(get_session)) -> Applicant:
    
    # Validate the positions limit before creating
    validate_positions_limit(session, applicant_id=None, new_positions=applicant_data.positions)
    
    applicant = Applicant.model_validate(applicant_data)
    
    if applicant_data.experience:
        for experience in applicant_data.experience:
            experience_obj = Experience(
                title=experience.title, 
                description=experience.description, 
                applicant=applicant
            )  # build relationship with applicant
            session.add(experience_obj)
    
    session.add(applicant)
    session.commit()  # after commit() will get id, then refresh to get all the data including primary key
    session.refresh(applicant)
    return applicant


@router.patch("/applicants/{applicant_id}", response_model=Applicant)
async def update_applicant(applicant_id: Annotated[int, Path(title="The Applicant ID. Updated by Admin")],
                           updated_applicant: ApplicantUpdate,
                           session: Session = Depends(get_session)) -> Applicant:
    db_applicant = session.get(Applicant, applicant_id)

    if db_applicant is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"The applicant with id {applicant_id} is not found")
   
    # Fetch the current and new positions
    new_positions = updated_applicant.positions or []
    validate_positions_limit(session, applicant_id, new_positions)

    applicant_data = updated_applicant.model_dump(exclude_unset=True)
    db_applicant.sqlmodel_update(applicant_data)
    session.add(db_applicant)
    session.commit()
    session.refresh(db_applicant)
    
    return db_applicant



# limit user can only vote five application no matter it is first priority or second.





# if user is applicant
@router.post("/users", status_code=status.HTTP_201_CREATED, response_model=User)
async def create_user(user_data: UserCreate, session: Session = Depends(get_session)) -> User:
    user = User(**user_data.dict())
    session.add(user)
    session.commit()
    
    if user.if_applicant:
        applicant = Applicant(user_id=user.id, fname=user.fname, lname=user.lname, email=user.email)
        session.add(applicant)
        session.commit()
    
    session.refresh(user)
    return user
