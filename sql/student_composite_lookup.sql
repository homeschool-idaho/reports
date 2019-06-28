SELECT DISTINCT score_student_data.region_num, score_student_data.f_name, score_student_data.l_name, 
member.street, member.city, member.state, member.zip, member.phone_home, student.student_id, score_npr.composite, testing_history.test_year, score_npr.score_id, testing_history.testing_history_id
FROM 
score_student_data, testing_history, member, student, score_npr 
WHERE 
score_student_data.student_id = student.student_id 
AND score_student_data.score_id   = score_npr.score_id 
AND student.member_id             = member.member_id 
AND student.student_id            = testing_history.student_id 
AND testing_history.grade >= 9
AND testing_history.test_year >= 2011
AND year( score_student_data.date_tested ) >= 2011
AND student.student_id = 7758
LIMIT 3000