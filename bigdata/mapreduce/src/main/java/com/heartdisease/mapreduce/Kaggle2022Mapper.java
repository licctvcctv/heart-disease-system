package com.heartdisease.mapreduce;

import java.io.IOException;
import java.util.List;
import org.apache.hadoop.io.LongWritable;
import org.apache.hadoop.io.NullWritable;
import org.apache.hadoop.io.Text;
import org.apache.hadoop.mapreduce.Mapper;

public class Kaggle2022Mapper extends Mapper<LongWritable, Text, NullWritable, Text> {
    private final Text output = new Text();

    @Override
    protected void map(LongWritable key, Text value, Context context) throws IOException, InterruptedException {
        String line = value.toString();
        if (line.startsWith("State,Sex,GeneralHealth,")) {
            return;
        }
        List<String> row = CsvRecordParser.parse(line);
        if (row.size() < 40) {
            return;
        }

        String riskLabel = "yes".equalsIgnoreCase(MapperSupport.value(row, 9))
            || "yes".equalsIgnoreCase(MapperSupport.value(row, 10)) ? "1" : "0";

        output.set(MapperSupport.tsv(
            "kaggle_2022",
            riskLabel,
            MapperSupport.value(row, 29),
            MapperSupport.sexCode(MapperSupport.value(row, 1)),
            MapperSupport.numeric(row, 32),
            MapperSupport.intNumeric(row, 3),
            MapperSupport.intNumeric(row, 4),
            MapperSupport.smokerStatusFlag(MapperSupport.value(row, 25)),
            MapperSupport.yesNo(MapperSupport.value(row, 33)),
            MapperSupport.yesNo(MapperSupport.value(row, 6)),
            MapperSupport.numeric(row, 7),
            MapperSupport.yesNo(MapperSupport.value(row, 11)),
            MapperSupport.diabetesFlag(MapperSupport.value(row, 18)),
            MapperSupport.yesNo(MapperSupport.value(row, 16)),
            MapperSupport.yesNo(MapperSupport.value(row, 12)),
            MapperSupport.yesNo(MapperSupport.value(row, 13)),
            MapperSupport.NULL_VALUE,
            MapperSupport.NULL_VALUE,
            MapperSupport.NULL_VALUE,
            MapperSupport.NULL_VALUE,
            MapperSupport.NULL_VALUE,
            MapperSupport.NULL_VALUE,
            MapperSupport.NULL_VALUE,
            MapperSupport.NULL_VALUE,
            MapperSupport.NULL_VALUE
        ));
        context.write(NullWritable.get(), output);
    }
}
