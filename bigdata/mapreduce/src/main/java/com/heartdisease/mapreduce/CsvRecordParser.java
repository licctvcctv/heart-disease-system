package com.heartdisease.mapreduce;

import java.io.IOException;
import java.util.ArrayList;
import java.util.List;
import org.apache.commons.csv.CSVFormat;
import org.apache.commons.csv.CSVParser;
import org.apache.commons.csv.CSVRecord;

final class CsvRecordParser {
    private CsvRecordParser() {
    }

    static List<String> parse(String line) throws IOException {
        try (CSVParser parser = CSVParser.parse(line, CSVFormat.DEFAULT)) {
            for (CSVRecord record : parser) {
                List<String> values = new ArrayList<>();
                record.forEach(values::add);
                return values;
            }
        }
        return List.of();
    }
}
