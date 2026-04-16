package com.heartdisease.mapreduce;

import java.io.IOException;
import java.util.List;
import org.apache.hadoop.io.LongWritable;
import org.apache.hadoop.io.NullWritable;
import org.apache.hadoop.io.Text;
import org.apache.hadoop.mapreduce.Mapper;

public class UciClevelandMapper extends Mapper<LongWritable, Text, NullWritable, Text> {
    private final Text output = new Text();

    @Override
    protected void map(LongWritable key, Text value, Context context) throws IOException, InterruptedException {
        String line = value.toString();
        if (line.trim().isEmpty()) {
            return;
        }
        List<String> row = CsvRecordParser.parse(line);
        if (row.size() < 14) {
            return;
        }

        output.set(MapperSupport.tsv(
            "uci_cleveland",
            MapperSupport.riskFromDiagnosis(MapperSupport.value(row, 13)),
            MapperSupport.ageBandFromNumber(MapperSupport.value(row, 0)),
            MapperSupport.sexCode(MapperSupport.value(row, 1)),
            MapperSupport.NULL_VALUE,
            MapperSupport.NULL_VALUE,
            MapperSupport.NULL_VALUE,
            MapperSupport.NULL_VALUE,
            MapperSupport.NULL_VALUE,
            MapperSupport.NULL_VALUE,
            MapperSupport.NULL_VALUE,
            MapperSupport.NULL_VALUE,
            MapperSupport.NULL_VALUE,
            MapperSupport.NULL_VALUE,
            MapperSupport.NULL_VALUE,
            MapperSupport.NULL_VALUE,
            MapperSupport.intNumeric(row, 2),
            MapperSupport.numeric(row, 3),
            MapperSupport.numeric(row, 4),
            MapperSupport.numeric(row, 7),
            MapperSupport.intNumeric(row, 8),
            MapperSupport.numeric(row, 9),
            MapperSupport.intNumeric(row, 10),
            MapperSupport.intNumeric(row, 11),
            MapperSupport.intNumeric(row, 12)
        ));
        context.write(NullWritable.get(), output);
    }
}
