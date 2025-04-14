from collections import deque, OrderedDict


def FIFO(pages, frame_count):
    if frame_count <= 0:
        return 0, 0, 0, []
    
    l = len(pages)

    memory = ['_'] * frame_count
    faults = 0
    hits = 0
    states = []
    
    indx = 0

    for page in pages:
        if page in memory:
            hits = hits + 1
        else:
            memory[indx % frame_count] = page
            indx = indx + 1
            faults = faults + 1
        states.append(memory.copy())
    
    hit_ratio = hits / l
    return faults, hits, hit_ratio, states



def LRU(pages, frame_count):
    if frame_count <= 0:
        return 0, 0, 0, []
    
    memory_tracker = OrderedDict()
    memory_frames = ['_'] * frame_count
    memory_history = []
    
    faults = 0
    hits = 0
    
    for page in pages:
        if page in memory_tracker:
            memory_tracker.move_to_end(page)
            hits += 1
        else:
            faults += 1
            
            if len(memory_tracker) >= frame_count:
                oldest_page, _ = memory_tracker.popitem(last=False)
                memory_frames[memory_frames.index(oldest_page)] = page
            else:
                empty_index = memory_frames.index('_')
                memory_frames[empty_index] = page
                
            memory_tracker[page] = True
            
        memory_history.append(memory_frames.copy())
    
    hit_ratio = hits / len(pages) if pages else 0
    
    return faults, hits, hit_ratio, memory_history

def Optimal(pages, frame_count):
    if frame_count <= 0:
        return 0, 0, 0, []
    
    frames = ['-'] * frame_count
    frame_history = []
    
    future_use_display = [''] * frame_count
    future_history = []
    
    page_count = len(pages)
    future_references = {}
    
    for i, page in enumerate(pages):
        if page not in future_references:
            future_references[page] = []
        future_references[page].append(i)
    
    fault_counter = 0
    hit_counter = 0
    
    for current_pos, page in enumerate(pages):
        for p in future_references:
            while future_references[p] and future_references[p][0] < current_pos:
                future_references[p].pop(0)
        
        if page in frames:
            hit_counter += 1
        else:
            fault_counter += 1
            
            if '-' in frames:
                position = frames.index('-')
                frames[position] = page
            else:
                max_future = -1
                replace_position = 0
                
                for i, current_page in enumerate(frames):
                    if not future_references[current_page]:
                        replace_position = i
                        break
                    
                    if future_references[current_page][0] > max_future:
                        max_future = future_references[current_page][0]
                        replace_position = i
                
                frames[replace_position] = page
        
        for i, p in enumerate(frames):
            if p != '-':
                future_use_display[i] = (future_references[p][0] 
                                        if future_references[p] 
                                        else 'inf')
            else:
                future_use_display[i] = ''
        
        frame_history.append(frames.copy())
        future_history.append(future_use_display.copy())
        
        if page in future_references and future_references[page]:
            future_references[page].pop(0)
    
    hit_ratio = hit_counter / page_count if page_count > 0 else 0
    
    return fault_counter, hit_counter, hit_ratio, frame_history, future_history