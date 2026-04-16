package com.heartdisease.mapreduce;

import java.util.Locale;
import org.apache.hadoop.conf.Configuration;
import org.apache.hadoop.fs.Path;
import org.apache.hadoop.io.NullWritable;
import org.apache.hadoop.io.Text;
import org.apache.hadoop.mapreduce.Job;
import org.apache.hadoop.mapreduce.Mapper;
import org.apache.hadoop.mapreduce.lib.input.FileInputFormat;
import org.apache.hadoop.mapreduce.lib.output.FileOutputFormat;

public class HeartEtlJob {
    public static void main(String[] args) throws Exception {
        if (args.length != 3) {
            System.err.println("Usage: HeartEtlJob <kaggle2020|kaggle2022|uci> <input> <output>");
            System.exit(2);
        }

        String dataset = args[0].toLowerCase(Locale.ROOT);
        Class<? extends Mapper> mapperClass = mapperFor(dataset);

        Configuration conf = new Configuration();
        Job job = Job.getInstance(conf, "heart-disease-etl-" + dataset);
        job.setJarByClass(HeartEtlJob.class);
        job.setMapperClass(mapperClass);
        job.setNumReduceTasks(0);

        job.setOutputKeyClass(NullWritable.class);
        job.setOutputValueClass(Text.class);

        FileInputFormat.addInputPath(job, new Path(args[1]));
        FileOutputFormat.setOutputPath(job, new Path(args[2]));

        System.exit(job.waitForCompletion(true) ? 0 : 1);
    }

    private static Class<? extends Mapper> mapperFor(String dataset) {
        switch (dataset) {
            case "kaggle2020":
                return Kaggle2020Mapper.class;
            case "kaggle2022":
                return Kaggle2022Mapper.class;
            case "uci":
            case "cleveland":
                return UciClevelandMapper.class;
            default:
                throw new IllegalArgumentException("Unsupported dataset: " + dataset);
        }
    }
}
