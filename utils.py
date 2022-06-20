def pagination(query, page_number, page_size):
    '''
    Функция принимает orm-query со списком записей и накладывает на него пагинацию
    '''
    return query.limit(page_size).offset((page_number - 1) * page_size)
