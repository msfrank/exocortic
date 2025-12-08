
set_property(GLOBAL PROPERTY curr_generated_target_index "0")

function(generate_target_name TARGET_VAR)
    get_property(curr_index GLOBAL PROPERTY curr_generated_target_index)
    set(${TARGET_VAR} "xoco_generated_target_${curr_index}")
    math(EXPR next_index "${curr_index} + 1")
    set_property(GLOBAL PROPERTY curr_generated_target_index "${next_index}")
    return(PROPAGATE ${TARGET_VAR})
endfunction()
