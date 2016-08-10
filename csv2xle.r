library(magrittr)
library(xml2)

create_section <- function(x, title, names, values) {
    title = xml_add_child(x, title)
    if (length(names) != length(values)) {
        browser()
        stop("Different lengths of names and values.")
    }
    if (length(names) > 0) {
        tmp = xml_add_child(title, names[1], values[1])
        if (length(x) > 1) {
            for (n in length(names):2)
                xml_add_sibling(tmp, names[n], values[n])
        }
    }
}

csv2xle <- function(file, dir) {
    if (missing(dir))
        dir_file = file
    else
        dir_file = file.path(dir, file)
    cat(paste0(dir_file, "\n"))
    meta = readLines(dir_file, 50, encoding = "latin1")
    init_data = grep("Date;Time", meta, fixed = TRUE)
    is_offset = any(grepl("Offset", meta, fixed = TRUE))
    meta = meta[1:init_data]
    dta = read.csv(dir_file, skip = init_data - 1, sep = ";", stringsAsFactors = FALSE, fileEncoding = "latin1")

    x = xml_new_document(version = "1.0")
    body = xml_add_child(x, "Body_xle")

    create_section(body, "File_info",
        c("Company", "LICENCE", "Date", "Time", "FileName", "Created_by"),
        c("", "", dta$Date[nrow(dta)], dta$Time[nrow(dta)], "", "Levelogger Software Version 4"))

    create_section(body, "Instrument_info",
        c("Instrument_type", "Model_number", "Instrument_state", "Serial_number", "Battery_level", "Channel", "Firmware"),
        c("LT_EDGE", "M5      ", "Stopped", meta[2], 100, 2, "3,002"))

    create_section(body, "Instrument_info_data_header",
        c("Project_ID", "Location", "Latitude", "Longtitude", "Sample_rate", "Sample_mode", "Event_ch", "Event_threshold",
            "Schedule", "Start_time", "Stop_time", "Num_log"),
        c(meta[4], meta[6], "0,000", "0,000", "360000", "0", "0", "0,000000",
            "", paste(dta$Date[1], dta$Time[1]), paste(dta$Date[nrow(dta)], dta$Time[nrow(dta)]), nrow(dta)))

    create_section(body, "Ch1_data_header",
        c("Identification", "Unit", "Parameters"),
        c(meta[7], conv_degree(unlist(strsplit(meta[8], " "))[2]), ""))

    create_section(body, "Ch2_data_header",
        c("Identification", "Unit", "Parameters"),
        c(meta[9 + is_offset], conv_degree(unlist(strsplit(meta[10 + is_offset], " "))[2]), ""))

    if (is_offset) {
        params = xml_find_first(body, "//Parameters")
        offset = unlist(strsplit(meta[9], " "))
        xml_add_child(params, "Offset", Val = offset[2], Unit = conv_degree(offset[3]))
    }

    dta_node = xml_add_child(body, "Data")

    for (r in 1:nrow(dta)) {
        log = xml_add_child(dta_node, "Log", id = as.character(r))
        xml_add_child(log, "Date", dta$Date[r])
        xml_add_child(log, "Time", dta$Time[r])
        xml_add_child(log, "ms", dta$ms[r])
        xml_add_child(log, "ch1", dta[[4]][r])
        xml_add_child(log, "ch2", dta[[5]][r])
    }

    write_xml(x, gsub(".csv", ".xle", dir_file, fixed = TRUE))
}

dir = "zzzprevod"
files = list.files(dir)
files = files[gsub(".csv", "", files, fixed = TRUE) != files]
for (file in files) {
    csv2xle(file, dir)
}
# csv2xle("Oles_H.csv")
